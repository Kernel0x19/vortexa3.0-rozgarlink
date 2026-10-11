export default function ApplicationsPage() {
  return (
    <div className="flex flex-col gap-6 max-w-300 transition-all duration-500">
      <div>
        <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-xl">My Applications</p>
        <p className="font-mono text-[14px] text-gray-400 dark:text-[#6B7280] mt-1">
          Track your application status across all opportunities
        </p>
      </div>
      {/* ApplicationsClient component renders here */}
    </div>
  );
}
