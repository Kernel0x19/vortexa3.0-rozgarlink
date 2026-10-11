export default function SkillGapsPage() {
  return (
    <div className="flex flex-col gap-6 max-w-300 transition-all duration-500">
      <div>
        <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-xl">Skill Gaps</p>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
          Skills you need for saved or interested opportunities · Suggested learning pathways
        </p>
      </div>
      {/* SkillGapsClient component renders here */}
    </div>
  );
}
