// Date utility functions — pure, no React dependencies

export function formatDate(
  dateString: string,
  locale: string = 'en',
  options: Intl.DateTimeFormatOptions = { dateStyle: 'medium' },
): string {
  return new Intl.DateTimeFormat(locale, options).format(new Date(dateString));
}

export function formatDateTime(dateString: string, locale: string = 'en'): string {
  return formatDate(dateString, locale, { dateStyle: 'medium', timeStyle: 'short' });
}

export function formatTime(dateString: string, locale: string = 'en'): string {
  return formatDate(dateString, locale, { timeStyle: 'short' });
}

export function isToday(dateString: string): boolean {
  const date = new Date(dateString);
  const today = new Date();
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
}

export function toISODateString(date: Date): string {
  return date.toISOString().split('T')[0];
}
