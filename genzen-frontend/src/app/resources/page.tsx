import { getResourcesContent } from '@/utils/content';
import type { Privacy, Resources } from '@/types/about';

// Helper function to convert URLs in text to clickable links
const convertUrlsToLinks = (text: string) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.split(urlRegex).map((part, index) => {
        if (part.match(urlRegex)) {
            return (
                <a
                    key={index}
                    href={part}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 hover:underline"
                >
                    {part}
                </a>
            );
        }
        return part;
    });
};

// Helper function to convert dashes into ordered list items
const convertToOrderedList = (content: string) => {
    const lines = content.split('\n');
    const listItems = lines.filter(line => line.trim().startsWith('-'));
    const nonListContent = lines.filter(line => !line.trim().startsWith('-')).join('\n');

    return (
        <>
            {nonListContent && <div className="mb-4">{convertUrlsToLinks(nonListContent)}</div>}
            {listItems.length > 0 && (
                <ol className="list-decimal list-inside space-y-2">
                    {listItems.map((item, index) => (
                        <li key={index} className="text-gray-700">
                            {convertUrlsToLinks(item.replace(/^- /, ''))}
                        </li>
                    ))}
                </ol>
            )}
        </>
    );
};

export default async function Resources() {
    const resources = await getResourcesContent();

    return (
        <section className="mb-12">
            <h1 className="text-2xl sm:text-3xl font-semibold mb-6 text-gray-800">{resources.title}</h1>
            <div className="bg-white/80 rounded-lg p-6 shadow-lg space-y-8">
                <p className="text-sm text-gray-600 mb-6">Last updated: {resources.lastUpdated}</p>
                
                {resources.sections.map((section: Resources['sections'][0], index: number) => (
                    <div key={index} className="space-y-4">
                        <h2 className="text-xl font-semibold text-gray-800">{section.title}</h2>
                        <div className="text-gray-700">
                            {convertToOrderedList(section.content)}
                        </div>
                        {section.source && (
                            <div className="mt-4 pt-4 border-t border-gray-200">
                                <p className="text-sm text-gray-500 italic">
                                    {convertUrlsToLinks(section.source)}
                                </p>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </section>
    );
}