/** Mirrors backend app/schemas/face.py → FaceStatusResponse */
export interface FaceStatus {
  employee_id: string;
  enrolled: boolean;
  samples: number;
}

/** Mirrors backend app/schemas/face.py → FaceEnrollResponse */
export interface FaceEnrollResult {
  employee_id: string;
  samples_captured: number;
  message: string;
}

/** Steps of the guided capture flow shown inside the camera modal. */
export type CapturePhase =
  | 'requesting-camera'
  | 'positioning'
  | 'countdown'
  | 'captured'
  | 'uploading'
  | 'success'
  | 'error';

/** A single captured frame, ready to be sent to the backend. */
export interface CapturedSample {
  index: number;
  base64: string;
}
