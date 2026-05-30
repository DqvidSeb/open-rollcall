// Toast — stub, to be implemented with a portal + animation
export interface ToastMessage {
  id: string;
  message: string;
  variant: 'success' | 'error' | 'info' | 'warning';
}

interface ToastProps {
  toast: ToastMessage;
  onDismiss: (id: string) => void;
}

export function Toast(_props: ToastProps) {
  // TODO: implement
  return null;
}

export function ToastContainer(_props: { toasts: ToastMessage[] }) {
  // TODO: implement portal-based container
  return null;
}
