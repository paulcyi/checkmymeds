'use client';

import { useState } from 'react';

export default function Home() {
  const [drug1, setDrug1] = useState('');
  const [drug2, setDrug2] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleCheck = async () => {
    if (!drug1 || !drug2) return;

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch('http://localhost:8000/api/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ drug1, drug2 }),
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setResult({ status: 'error', message: 'Failed to fetch interaction data.' });
    } finally {
      setLoading(false);
    }
  };

  const generateSummaryForFrontend = (highlightedTexts: any): string => {
    const flatText = Object.values(highlightedTexts).flat().join(' ').toLowerCase();

    if (flatText.includes('bleed')) return 'This combo may increase bleeding risk.';
    if (flatText.includes('liver')) return 'Possible liver toxicity.';
    if (flatText.includes('serotonin')) return 'May raise serotonin dangerously (serotonin syndrome).';
    if (flatText.includes('cns')) return 'May increase sedation or CNS depression.';
    if (flatText.includes('respiratory')) return 'May slow down breathing (respiratory depression).';
    if (flatText.includes('renal') || flatText.includes('kidney')) return 'May impair kidney function.';

    return 'This label combination may increase risk of side effects. Monitor closely.';
  };

  return (
    <main className="min-h-screen bg-cmm-surface text-gray-900 dark:bg-cmm-surface-900 dark:text-white p-6">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-cmm-primary-600">💊 CheckMyMeds</h1>

        <div className="rounded p-4 bg-cmm-primary-500 text-white">
          ✅ Tailwind token works — this box is teal
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <input
            className="w-full p-2 border rounded dark:bg-gray-800"
            value={drug1}
            onChange={(e) => setDrug1(e.target.value)}
            placeholder="First drug"
          />
          <input
            className="w-full p-2 border rounded dark:bg-gray-800"
            value={drug2}
            onChange={(e) => setDrug2(e.target.value)}
            placeholder="Second drug"
          />
        </div>

        <button
          className="bg-cmm-accent-600 hover:bg-cmm-accent-700 text-white px-4 py-2 rounded disabled:opacity-50"
          onClick={handleCheck}
          disabled={loading}
        >
          {loading ? 'Checking...' : 'Check Interaction'}
        </button>

        {/* RxNav interaction results */}
        {result?.status === 'success' && result.interactions?.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Interactions Found</h2>
            {result.interactions.map((interaction: any, index: number) => (
              <div
                key={index}
                className="p-4 rounded border dark:border-gray-700 bg-gray-50 dark:bg-gray-800"
              >
                <p className="mb-1 text-sm text-gray-600 dark:text-gray-300">
                  <span className="font-semibold">Severity:</span>{' '}
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-white text-xs ${interaction.severity === 'High'
                        ? 'bg-cmm-severity-severe'
                        : interaction.severity === 'Moderate'
                          ? 'bg-cmm-severity-mod'
                          : 'bg-cmm-severity-mild'
                      }`}
                  >
                    {interaction.severity}
                  </span>
                </p>
                <p className="mb-1 text-sm">
                  <span className="font-semibold">Description:</span>{' '}
                  {interaction.description}
                </p>
                <p className="text-sm text-gray-500">
                  <span className="font-semibold">Source:</span> {interaction.source}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* No interactions */}
        {result?.status === 'success' && result.interactions?.length === 0 && (
          <p className="mt-6 text-sm text-green-700 dark:text-green-400">
            ✅ No known interactions found.
          </p>
        )}

        {/* OpenFDA fallback */}
        {result?.status === 'label_mentions' && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-yellow-600 dark:text-yellow-400">
              ⚠️ Potential label-based interactions (OpenFDA fallback)
            </h2>
            {result.mentions.map((mention: any, index: number) => {
              const entries = Object.entries(mention.results.highlighted_texts) as [string, string[]][];
              return (
                <div
                  key={index}
                  className="p-4 border rounded bg-yellow-50 dark:bg-yellow-900 border-yellow-300 dark:border-yellow-700"
                >
                  <h3 className="text-md font-semibold mb-2">
                    {mention.sourceDrug} mentions {mention.mentionedDrug} in its label
                  </h3>

                  {entries.map(([section, texts], sectionIdx) => (
                    <div key={sectionIdx} className="mb-2">
                      <p className="font-semibold text-sm capitalize text-gray-700 dark:text-gray-300">
                        {section.replace(/_/g, ' ')}
                      </p>
                      {texts.map((text, textIdx) => (
                        <div
                          key={textIdx}
                          className="bg-white dark:bg-gray-800 border-l-4 border-yellow-400 pl-4 py-2 mb-1 text-sm"
                          dangerouslySetInnerHTML={{ __html: text }}
                        />
                      ))}
                    </div>
                  ))}

                  <div className="mt-2 text-sm italic text-gray-700 dark:text-gray-300">
                    🧠 Summary:{' '}
                    {mention.results.highlighted_texts &&
                      generateSummaryForFrontend(mention.results.highlighted_texts)}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Error */}
        {result?.status === 'error' && (
          <p className="mt-6 text-sm text-red-600 dark:text-red-400">
            ⚠️ {result.message}
          </p>
        )}
      </div>
    </main>
  );
}
