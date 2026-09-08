const sections = [
  {
    id: "sensors",
    title: "Sensors",
  },
  {
    id: "config",
    title: "Configuration",
  },
  {
    id: "automation",
    title: "Automation",
  },
  {
    id: "overview",
    title: "Overview",
  },
  {
    id: "controls",
    title: "Controls",
  },
  {
    id: "events",
    title: "Events",
  },
];

export default function DashboardPage() {
  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-slate-900">
          Dashboard
        </h2>

        <p className="mt-2 text-slate-600">
          Smart Greenhouse monitoring and control dashboard.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {sections.map((section) => (
          <section
            key={section.id}
            id={section.id}
            className="min-h-40 rounded-xl border bg-white p-6 shadow-sm"
          >
            <h3 className="text-lg font-semibold text-emerald-700">
              {section.title}
            </h3>

            <p className="mt-2 text-sm text-slate-500">
              Placeholder for the {section.title.toLowerCase()} section.
            </p>
          </section>
        ))}
      </div>
    </div>
  );
}