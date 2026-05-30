// Dropdown — stub, to be implemented
interface DropdownItem {
  key: string;
  label: string;
  onClick: () => void;
  disabled?: boolean;
  danger?: boolean;
}

interface DropdownProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  align?: 'left' | 'right';
}

export function Dropdown(_props: DropdownProps) {
  // TODO: implement with outside-click detection
  return null;
}
