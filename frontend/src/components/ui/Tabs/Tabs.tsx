// Tabs — stub, to be implemented
interface Tab {
  key: string;
  label: string;
  content: React.ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
}

export function Tabs(_props: TabsProps) {
  // TODO: implement with keyboard navigation
  return null;
}
