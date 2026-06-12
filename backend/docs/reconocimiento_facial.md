# Reconocimiento facial en RollCall — arquitectura y pipeline

## 1. Resumen técnico

El sistema implementa **face recognition basado en embeddings**, usando un
modelo de **deep learning pre-entrenado**: una **red neuronal convolucional
(CNN)** llamada **ArcFace**, servida a través de la librería `DeepFace`. El
backend no entrena ni reentrena ningún modelo: usa ArcFace como **extractor
de características fijo** (feature extractor), y la lógica de identificación
se resuelve con **k-Nearest Neighbors (k-NN)** sobre distancia coseno,
calculado con `pgvector` en PostgreSQL.

Dos componentes, dos algoritmos distintos:

| Etapa | Algoritmo | Tipo |
|---|---|---|
| Imagen → vector de 512 dimensiones | ArcFace (CNN, ResNet-based) | Deep Learning, modelo pre-entrenado |
| Vector → identidad | k-NN + distancia coseno + votación | Machine Learning clásico |

### Glosario de esta sección

| Término | Explicación |
|---|---|
| **Embedding** | Es la "huella" matemática de una cara: una lista ordenada de 512 números decimales. Dos caras de la misma persona producen listas de números muy parecidas entre sí; caras de personas distintas producen listas claramente diferentes. El sistema nunca compara fotos directamente — siempre compara estas listas de números. |
| **Face recognition basado en embeddings** | Es el enfoque general: en lugar de que el sistema "mire" la foto y decida quién es, primero convierte la foto en un embedding, y luego compara ese embedding contra los embeddings ya guardados de cada persona. Reconocer a alguien se reduce a un problema de comparar listas de números, que es algo que las computadoras hacen muy rápido. |
| **Deep learning** | Es una rama del aprendizaje automático donde el modelo está formado por muchas capas apiladas de operaciones matemáticas (de ahí "profundo" / *deep*). Cada capa recibe la salida de la anterior y extrae información cada vez más abstracta. ArcFace es un modelo de deep learning. |
| **Modelo pre-entrenado** | Significa que ArcFace ya fue entrenado por terceros, usando millones de fotos de rostros de cientos de miles de personas distintas, antes de que este proyecto existiera. RollCall no entrena ArcFace ni le muestra ejemplos para "aprender" — simplemente lo usa tal como viene, ya que aprendió de forma general cómo distinguir rasgos faciales entre personas distintas (cualquier persona, no solo las que ya conoce). |
| **Red neuronal convolucional (CNN)** | CNN = *Convolutional Neural Network*. Es un tipo de red neuronal especializada en procesar imágenes. Funciona aplicando "filtros" (operaciones llamadas convoluciones) que recorren la imagen detectando patrones: primero patrones simples (bordes, contrastes, texturas), y al combinarlos en capas posteriores, patrones cada vez más complejos (forma de los ojos, distancia entre ellos, contorno de la mandíbula, etc.). El resultado final de todas esas capas es el embedding de 512 números. |
| **Extractor de características fijo** | Quiere decir que ArcFace se usa "tal cual viene", sin modificar sus parámetros internos. Solo se le pasa una imagen y se recibe el embedding como salida; el modelo no cambia ni aprende nada nuevo durante el uso del sistema. |
| **k-Nearest Neighbors (k-NN)** | Es un algoritmo clásico (no es una red neuronal) que responde la pregunta "¿cuáles son los *k* elementos más parecidos a este, de entre todos los que tengo guardados?". En este sistema, dado el embedding de la cara que se está viendo en este momento, k-NN busca los 10 embeddings más parecidos (k=10) entre todos los que están guardados en la base de datos, sin importar a qué persona pertenezcan. |
| **Distancia coseno** | Es la fórmula que k-NN usa para medir "qué tan parecidos" son dos embeddings. Cada embedding se puede pensar como una flecha que apunta en una dirección dentro de un espacio de 512 dimensiones. La distancia coseno mide el ángulo entre dos flechas: si apuntan casi en la misma dirección, el valor es cercano a 0 (muy parecidas); si apuntan en direcciones muy distintas, el valor se acerca a 2 (muy diferentes). Es una medida de *dirección*, no de tamaño — por eso funciona bien aunque la "intensidad" del embedding varíe un poco entre fotos. |
| **pgvector** | Es una extensión de PostgreSQL que agrega un tipo de dato especial (`vector`) para guardar listas de números como los embeddings, junto con operadores que calculan distancias (incluyendo la distancia coseno) directamente dentro de la base de datos, de forma optimizada. En el código del proyecto, esto se usa así: el embedding se guarda en una columna de tipo `vector(512)` en la tabla `face_encoding`, y cuando se necesita comparar, se ejecuta una consulta SQL que ordena todas las filas por distancia coseno respecto al embedding actual y devuelve las 10 más cercanas. |

---

## 2. Pipeline de enrollment

"Enrollment" es el proceso de registrar el rostro de una persona por primera
vez (o de actualizarlo), para que el sistema pueda reconocerla más adelante.

### 2.1 Captura

El sistema captura **5 imágenes** de la cara de la persona en el momento del
registro. Esto no es arbitrario: cada foto individual va a tener pequeñas
diferencias — un ligero cambio de ángulo de la cabeza, una variación en la
iluminación del lugar, una expresión facial distinta (sonriendo, serio,
etc.). Si el sistema guardara una sola foto, esas pequeñas diferencias entre
"la foto de registro" y "la foto que se toma después en la cámara de
asistencia" podrían hacer que el embedding generado en el momento del check-in
no coincida tan bien con el de registro, aunque sea la misma persona.

A esa variación natural entre distintas fotos de la **misma persona** se le
llama **varianza intra-clase** ("intra-clase" porque ocurre *dentro* del
grupo de fotos de una sola persona, no entre personas distintas). Guardando 5
muestras en lugar de 1, el sistema tiene varios "puntos de referencia" para
esa persona en el espacio de 512 dimensiones, en vez de un único punto que
podría no ser representativo. Esto se traduce en que, en la tabla
`face_encoding`, cada persona queda representada por una pequeña "nube" de 5
vectores cercanos entre sí, en lugar de un único vector — lo cual hace la
comparación posterior más tolerante a esas variaciones normales entre fotos.

### 2.2 Detección y alineación del rostro

Antes de poder calcular el embedding, el sistema necesita **encontrar la cara
dentro de la imagen** y **recortarla correctamente**. Esto lo hace un
**detector de rostros** (en este proyecto, YuNet u otro detector compatible
con OpenCV/DeepFace, configurable según el origen del frame).

El detector hace dos cosas:

1. Encuentra el rectángulo (bounding box) donde está la cara dentro de la
   imagen completa.
2. Encuentra puntos de referencia clave de la cara — la posición de los ojos,
   la nariz y la boca (landmarks).

Con esos puntos de referencia, el sistema rota y escala la imagen para que
los ojos queden siempre a la misma altura y a la misma distancia entre sí —
esto se llama **alineación facial**. El resultado es un recorte de la cara de
112×112 píxeles, siempre con una orientación y proporción estandarizada, que
es exactamente el formato que ArcFace espera recibir.

¿Por qué importa esto? Si dos fotos de la misma persona se le pasaran a
ArcFace con orientaciones muy distintas (una de frente, otra ladeada), los
embeddings resultantes podrían diferir más de lo esperado simplemente por la
geometría de la imagen, no porque la persona sea distinta. La alineación
elimina esa fuente de variación antes de que la imagen llegue a la red
neuronal.

Si el detector no encuentra ninguna cara en la imagen, el sistema rechaza esa
imagen (no genera ningún embedding) y le pide al cliente intentar de nuevo —
así se evita guardar o comparar "huellas" calculadas sobre fondos vacíos o
imágenes sin rostro.

### 2.3 Extracción del embedding (ArcFace)

Una vez que se tiene el rostro recortado y alineado, este se pasa por la red
neuronal **ArcFace**, que produce como salida un **embedding de 512
números**.

ArcFace es una arquitectura de tipo ResNet (una familia común de CNNs)
entrenada con una función de pérdida llamada **Additive Angular Margin Loss**
(de ahí el nombre "ArcFace"). De forma simplificada:

```
L = -log( e^(s·cos(θ_yi + m)) / (e^(s·cos(θ_yi + m)) + Σ_{j≠yi} e^(s·cos(θ_j))) )
```

| Término | Explicación |
|---|---|
| `θ_yi` | Es el ángulo entre el embedding generado y la "dirección típica" de la persona correcta, dentro del espacio de 512 dimensiones, durante el entrenamiento del modelo. |
| `m` (margen angular) | Es un valor extra que se le suma a ese ángulo durante el entrenamiento, a propósito, para forzar al modelo a dejar más "espacio de separación" entre personas distintas. |
| `s` | Un factor de escala que amplifica las diferencias entre ángulos, para que la función de pérdida sea más sensible a pequeños cambios. |
| `cos(θ_j)` | El parecido (en términos de ángulo) entre el embedding generado y las direcciones típicas de *todas las demás* personas del set de entrenamiento. |

El efecto práctico de entrenar con esta fórmula es que el modelo aprende a
ubicar los embeddings de manera que: las fotos de una misma persona queden
*angularmente muy juntas* entre sí, y las fotos de personas distintas queden
*angularmente bien separadas* — incluso para personas que el modelo nunca vio
durante su entrenamiento. Esa es la propiedad que permite usar ArcFace "tal
cual" para reconocer a David, María o Mariana, sin necesidad de
re-entrenarlo con sus fotos específicamente: el modelo ya generaliza el
concepto de "qué hace que dos caras sean de la misma persona" a partir de las
millones de caras con las que fue entrenado originalmente.

La salida final de este paso es, entonces, un vector de 512 números reales
(`R^512`).

### 2.4 Persistencia en la base de datos

Cada uno de los 5 embeddings generados se guarda como una fila en la tabla
`face_encoding`, con la siguiente información:

| Campo | Qué guarda |
|---|---|
| `person_id` | A qué persona pertenece este embedding (David, María, Mariana...). |
| `embedding` | El vector de 512 números, guardado en una columna de tipo `vector(512)` gracias a `pgvector`. |
| `sample_index` | Un número del 0 al 4 que identifica cuál de las 5 muestras es. |
| `model_name` | El nombre del modelo usado para generar ese embedding (`ArcFace`), para evitar comparar embeddings generados por modelos distintos. |
| `is_primary` | Marca cuál de las 5 muestras se considera la "principal" (la primera). |

Es importante resaltar que **no se guarda ninguna imagen**: solo se guardan
estos vectores de números. Por eso, aunque alguien tuviera acceso directo a
la base de datos, no podría reconstruir visualmente la cara de la persona a
partir de esa información — solo vería listas de 512 números decimales.

Si una persona ya tenía un rostro registrado previamente y se vuelve a
registrar (re-enrollment), el sistema primero **borra los 5 embeddings
anteriores** de esa persona antes de guardar los nuevos. Esto evita que
queden mezclados embeddings "viejos" (de una foto anterior, quizás con
distinta apariencia) junto con los nuevos, lo cual podría afectar la
precisión de las comparaciones futuras.

---

## 3. Pipeline de verificación / check-in

Esta es la fase que ocurre cada vez que una persona se para frente a la
cámara para marcar su asistencia.

### 3.1 Extracción del embedding actual

Se repite exactamente el mismo proceso descrito en 2.2 y 2.3 sobre el frame
capturado en este momento: detección del rostro, alineación, y paso por
ArcFace. El resultado es un embedding `q` de 512 números — la "huella" de la
cara que el sistema está viendo *ahora mismo*, que aún no se sabe a quién
pertenece.

### 3.2 Validaciones del vector antes de comparar

Antes de buscar coincidencias en la base de datos, el sistema hace dos
chequeos rápidos sobre el embedding `q`:

| Validación | Qué detecta |
|---|---|
| El vector tiene exactamente 512 números | Si tuviera otra cantidad, indicaría que el modelo configurado no es el esperado (configuración incorrecta). |
| Todos los números son valores finitos (sin `NaN` o `Infinito`) | Un embedding con valores inválidos no provoca un error visible en `pgvector`, sino que simplemente la búsqueda de coincidencias devuelve cero resultados sin explicación. Detectarlo antes permite mostrar un mensaje claro en vez de un fallo silencioso. |

### 3.3 Búsqueda de los más parecidos (k-NN por distancia coseno)

El sistema ejecuta una consulta sobre la tabla `face_encoding` que:

1. Calcula la distancia coseno entre el embedding actual `q` y **cada uno**
   de los embeddings guardados (de todas las personas registradas).
2. Ordena los resultados de menor a mayor distancia (más parecido primero).
3. Devuelve los **10 más parecidos**, sin importar a qué persona pertenezcan
   ni si son "lo bastante" parecidos todavía — esto se filtra en el paso
   siguiente.

La fórmula de la distancia coseno es:

```
d(a, b) = 1 - (a·b) / (||a|| ||b||)
```

| Término | Explicación |
|---|---|
| `a·b` | El producto punto entre los dos embeddings — una operación que combina ambos vectores en un solo número, que es mayor cuanto más "alineados" estén en la misma dirección. |
| `\|\|a\|\|`, `\|\|b\|\|` | La "longitud" (magnitud) de cada vector. Dividir por estas longitudes hace que el resultado dependa solo de la *dirección* de los vectores, no de su tamaño. |
| `d(a, b)` | El resultado final, en un rango de 0 a 2. `0` significa que los dos embeddings apuntan exactamente en la misma dirección (cara prácticamente idéntica); `2` significa que apuntan en direcciones opuestas (caras muy distintas). |

Se traen los 10 más cercanos sin aplicar todavía un umbral de "aceptación",
porque incluso si nadie coincide realmente, es útil saber **cuál fue el más
cercano y qué tan lejos estuvo** — esa información se usa más adelante tanto
para la respuesta al usuario como para ajustar la configuración del sistema.

### 3.4 Votación y decisión final

Con los 10 vecinos más cercanos en mano, el sistema decide a quién
corresponde la cara actual mediante estos pasos:

1. Se define un **umbral de distancia** fijo: `0.55`. Solo los embeddings con
   una distancia *menor* a ese valor se consideran "lo bastante parecidos"
   como para ser candidatos reales.
2. De los 10 vecinos, se agrupan por persona los que cumplen esa condición.
   Como cada persona tiene 5 embeddings guardados, es posible que varios de
   los 10 más cercanos pertenezcan a la misma persona.
3. Se cuenta cuántos "votos" recibe cada persona (cuántos de sus embeddings
   aparecieron entre los 10 más cercanos *y además* cumplieron el umbral).
4. **Gana la persona con más votos.** Si hay un empate en número de votos,
   gana la persona cuya muestra individual tuvo la menor distancia (la
   coincidencia más fuerte).
5. Si **ninguno** de los 10 vecinos cumple el umbral de 0.55, el sistema
   responde que no reconoció a nadie (`recognized = False`), pero igual
   informa cuál fue la persona más cercana y qué distancia obtuvo — esto sirve
   como diagnóstico, por ejemplo para detectar si el umbral está demasiado
   estricto o si la persona simplemente no está registrada.

Adicionalmente, se calcula un valor de **confianza** para mostrar en la
interfaz:

```
confianza = max(0, 1 - d/2)
```

Esto simplemente convierte la distancia (rango 0 a 2, donde menor es mejor) a
un valor entre 0 y 1 (donde mayor es mejor), para que sea más intuitivo de
leer como un "porcentaje de parecido". No es una probabilidad estadística
calibrada, sino una transformación directa de la distancia para fines de
visualización.

### 3.5 Registro de asistencia

Cuando el reconocimiento se hace específicamente para marcar asistencia (y no
solo como una previsualización de prueba), el resultado anterior —la persona
identificada, su nivel de confianza, etc.— se envía al servicio encargado de
asistencia, que decide si corresponde registrar una **entrada** o una
**salida** según el último evento registrado para esa persona, y guarda ese
evento junto con la confianza obtenida y el método usado (`face`).

---

## 4. Parámetros de configuración relevantes

| Parámetro | Valor | Efecto |
|---|---|---|
| Modelo de embedding | `ArcFace` | Modelo usado para generar los vectores de 512 dimensiones. |
| Detector facial en servidor | `retinaface` | Detector/alineador usado cuando el frame llega sin recortar previamente. |
| Umbral de distancia | `0.55` | Distancia coseno máxima para considerar que un embedding guardado coincide con el actual. |
| Exigencia de detección | `True` (activado) | Si está activo, el sistema rechaza frames donde no se detecta ningún rostro, en lugar de procesarlos igualmente. |
| Muestras por persona | `5` | Cantidad de imágenes capturadas durante el enrollment de cada persona. |

El umbral de distancia (`0.55`) es el parámetro más sensible del sistema, ya
que controla un compromiso (*trade-off*) entre dos tipos de error:

- **Bajarlo** hace al sistema más estricto: reduce el riesgo de confundir a
  dos personas distintas (falso positivo), pero aumenta el riesgo de no
  reconocer a la persona correcta si la foto actual varía un poco respecto a
  las de registro (falso negativo).
- **Subirlo** hace al sistema más permisivo: reconoce más fácilmente a la
  persona correcta incluso con variaciones, pero aumenta el riesgo de
  confundirla con otra persona parecida.

---

## 5. Mapeo a código

| Función | Ubicación |
|---|---|
| Extracción de embedding | `app/services/face_service.py::_extract_embedding` |
| Resolución de detector | `app/services/face_service.py::_resolve_detector` |
| Enrollment | `app/services/face_service.py::enroll` |
| Verificación + votación | `app/services/face_service.py::verify` |
| k-NN coseno | `app/repositories/face_encoding.py::find_nearest` |
| Modelo de embedding | `app/models/face_encoding.py` |
| Endpoints HTTP | `app/api/v1/endpoints/face.py` |
| Detección/alineación cliente (YuNet) | `backend/camera_client.py` |
| Configuración de parámetros | `app/core/config.py` |
