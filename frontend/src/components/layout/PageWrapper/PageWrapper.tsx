interface PageWrapperProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  children?: React.ReactNode;
}

export function PageWrapper({ title, description, action, children }: PageWrapperProps) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          {description && (
            <p className="text-sm text-gray-500 mt-1">{description}</p>
          )}
        </div>
        {action && <div>{action}</div>}
      </div>
      {children}
    </div>
  );
}
