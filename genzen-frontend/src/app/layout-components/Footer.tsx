import Link from 'next/link';

export default function Footer() {
    return (
        <footer className="bg-white border-t border-gray-200">
            <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <div className="flex flex-col md:flex-row justify-between items-center">
                    <div className="text-gray-500 text-sm mb-4 md:mb-0">
                        © {new Date().getFullYear()} GenZen. All rights reserved.
                    </div>
                    <div className="flex space-x-6">
                        <Link 
                            href="/terms" 
                            className="text-gray-500 hover:text-gray-700 text-sm"
                        >
                            Terms of Service
                        </Link>
                        <Link 
                            href="/privacy" 
                            className="text-gray-500 hover:text-gray-700 text-sm"
                        >
                            Privacy Policy
                        </Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
  