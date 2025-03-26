import { getPrivacyContent } from '@/utils/content';
import type { Privacy } from '@/types/about';

export default async function Privacy() {
    const privacy = getPrivacyContent();

    return (
        <section className="mb-12">
            <h1 className="text-2xl sm:text-3xl font-semibold mb-6 text-gray-800">{privacy.title}</h1>
            <div className="bg-white/80 rounded-lg p-6 shadow-lg space-y-8">
                <p className="text-sm text-gray-600 mb-6">Last updated: {privacy.lastUpdated}</p>
                
                {privacy.sections.map((section: Privacy['sections'][0], index: number) => (
                    <div key={index} className="space-y-4">
                        <h2 className="text-xl font-semibold text-gray-800">{section.title}</h2>
                        <div className="text-gray-700 whitespace-pre-line">
                            {section.content}
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
}