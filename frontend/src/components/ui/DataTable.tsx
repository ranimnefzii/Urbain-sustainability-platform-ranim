import LoadingSpinner from "./LoadingSpinner";
import EmptyState from "./EmptyState";

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  onRowClick?: (item: T) => void;
  keyExtractor: (item: T) => string | number;
  pagination?: {
    page: number;
    pages: number;
    total: number;
    onPageChange: (page: number) => void;
  };
}

export default function DataTable<T>({ columns, data, loading, emptyTitle, emptyDescription, onRowClick, keyExtractor, pagination }: DataTableProps<T>) {
  if (loading) return <LoadingSpinner size="lg" className="py-12" />;

  if (data.length === 0) {
    return <EmptyState title={emptyTitle || "No data found"} description={emptyDescription} />;
  }

  return (
    <div>
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col) => (
                <th key={col.key} className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${col.className || ""}`}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((item) => (
              <tr key={keyExtractor(item)} className={`${onRowClick ? "cursor-pointer hover:bg-gray-50" : ""}`} onClick={() => onRowClick?.(item)}>
                {columns.map((col) => (
                  <td key={col.key} className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 ${col.className || ""}`}>
                    {col.render ? col.render(item) : (item as any)[col.key] ?? "-"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pagination && pagination.pages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
          <p className="text-sm text-gray-700">
            Page <span className="font-medium">{pagination.page}</span> of <span className="font-medium">{pagination.pages}</span> ({pagination.total} total)
          </p>
          <nav className="flex gap-1">
            <button disabled={pagination.page <= 1} onClick={() => pagination.onPageChange(pagination.page - 1)}
              className="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">Previous</button>
            {Array.from({ length: Math.min(pagination.pages, 7) }, (_, i) => {
              let pageNum: number;
              if (pagination.pages <= 7) {
                pageNum = i + 1;
              } else if (pagination.page <= 4) {
                pageNum = i + 1;
              } else if (pagination.page >= pagination.pages - 3) {
                pageNum = pagination.pages - 6 + i;
              } else {
                pageNum = pagination.page - 3 + i;
              }
              return (
                <button key={pageNum} onClick={() => pagination.onPageChange(pageNum)}
                  className={`px-3 py-1 text-sm border rounded ${pageNum === pagination.page ? "bg-blue-600 text-white border-blue-600" : "hover:bg-gray-50"}`}>
                  {pageNum}
                </button>
              );
            })}
            <button disabled={pagination.page >= pagination.pages} onClick={() => pagination.onPageChange(pagination.page + 1)}
              className="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">Next</button>
          </nav>
        </div>
      )}
    </div>
  );
}
