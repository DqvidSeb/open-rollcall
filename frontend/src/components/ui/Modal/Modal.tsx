// Modal — stub, to be implemented with focus-trap and portal
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export function Modal(_props: ModalProps) {
  // TODO: implement with focus trap and scroll lock
  return null;
}
