export default function About() {
    return (
        <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl font-bold mb-8 text-gray-900 dark:text-white">About GenZen</h1>
            <div className="space-y-6">
                <p className="text-lg text-gray-700 dark:text-gray-300">
                    GenZen is an innovative AI-powered mental health support platform designed to provide 24/7 assistance
                    to those seeking emotional support and guidance. Our mission is to make mental health support
                    accessible, confidential, and helpful for everyone.
                </p>
                <p className="text-lg text-gray-700 dark:text-gray-300">
                    Using advanced artificial intelligence, we offer a safe space for users to express their thoughts
                    and feelings, receive supportive responses, and access helpful resources for mental well-being.
                </p>
                <div className="mt-8">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100">Our Features</h2>
                    <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
                        <li>24/7 AI-powered emotional support</li>
                        <li>Confidential and secure conversations</li>
                        <li>Evidence-based mental health resources</li>
                        <li>Personalized support experience</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}