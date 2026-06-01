interface StatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

const statusStyles: Record<string, string> = {
  SUBMITTED: "bg-yellow-100 text-yellow-800 border-yellow-300",
  PENDING: "bg-gray-100 text-gray-800 border-gray-300",
  UNDER_REVIEW: "bg-blue-100 text-blue-800 border-blue-300",
  ASSIGNED: "bg-indigo-100 text-indigo-800 border-indigo-300",
  IN_PROGRESS: "bg-cyan-100 text-cyan-800 border-cyan-300",
  RESOLVED: "bg-green-100 text-green-800 border-green-300",
  CLOSED: "bg-green-50 text-green-600 border-green-200",
  CANCELLED: "bg-red-100 text-red-800 border-red-300",
  REJECTED: "bg-red-100 text-red-800 border-red-300",
  ARCHIVED: "bg-gray-100 text-gray-500 border-gray-200",
  DRAFT: "bg-gray-50 text-gray-600 border-gray-200",
  PUBLISHED: "bg-green-100 text-green-800 border-green-300",
  SCHEDULED: "bg-purple-100 text-purple-800 border-purple-300",
  SENT: "bg-blue-100 text-blue-800 border-blue-300",
  FAILED: "bg-red-100 text-red-800 border-red-300",
  READ: "bg-green-100 text-green-800 border-green-300",
  UNREAD: "bg-blue-100 text-blue-800 border-blue-300",
  ACTIVE: "bg-green-100 text-green-800 border-green-300",
  INACTIVE: "bg-gray-100 text-gray-600 border-gray-300",
  PENDING_VERIFICATION: "bg-yellow-100 text-yellow-800 border-yellow-300",
  SUSPENDED: "bg-red-100 text-red-800 border-red-300",
  HIGH: "bg-red-100 text-red-800 border-red-300",
  MEDIUM: "bg-yellow-100 text-yellow-800 border-yellow-300",
  LOW: "bg-green-100 text-green-800 border-green-300",
  CRITICAL: "bg-red-200 text-red-900 border-red-400",
};

export default function StatusBadge({ status, size = "sm" }: StatusBadgeProps) {
  const style = statusStyles[status] || "bg-gray-100 text-gray-800 border-gray-300";
  return (
    <span className={`inline-flex items-center font-medium border rounded-full ${size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm"} ${style}`}>
      {status?.replace(/_/g, " ")}
    </span>
  );
}
