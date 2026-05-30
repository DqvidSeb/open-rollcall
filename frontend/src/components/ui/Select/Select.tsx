// Select — stub, to be implemented
interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  options: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
  label?: string;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
}

export function Select(_props: SelectProps) {
  // TODO: implement
  return null;
}
