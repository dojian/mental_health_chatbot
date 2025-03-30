export default function Home() {
    return (
        <>
            <h1 className="text-2xl sm:text-3xl font-semibold mb-6 text-gray-800 text-center">Welcome to GenZen</h1>
            <div className="bg-white/80 rounded-lg p-4 sm:p-6 shadow-lg">
                <div className="text-center space-y-6">
                    <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-800">
                        Your AI-powered mental health support companion
                    </h2>
                    <p className="text-lg sm:text-xl text-gray-700 max-w-2xl mx-auto">
                        GenZen is here to listen and support you through your college stresses and anxiety. 
                        We offer assistance in helping you find the right study habits, deciding your major, 
                        building your career, and more. 
                    </p>
                    <div className="mt-8 space-y-4">
                        <h3 className="text-xl sm:text-2xl font-semibold text-gray-800">Why Choose GenZen?</h3>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 max-w-3xl mx-auto">
                            <div className="bg-white/50 p-4 rounded-lg">
                                <h4 className="font-semibold text-gray-800 mb-2">24/7 Availability</h4>
                                <p className="text-gray-700">Get support anytime, anywhere, whenever you need someone to talk to.</p>
                            </div>
                            <div className="bg-white/50 p-4 rounded-lg">
                                <h4 className="font-semibold text-gray-800 mb-2">Confidential Support</h4>
                                <p className="text-gray-700">Your conversations are private and secure, ensuring a safe space for sharing.</p>
                            </div>
                            <div className="bg-white/50 p-4 rounded-lg">
                                <h4 className="font-semibold text-gray-800 mb-2">Personalized Care</h4>
                                <p className="text-gray-700">Receive tailored responses that address your unique situation and needs.</p>
                            </div>
                            <div className="bg-white/50 p-4 rounded-lg">
                                <h4 className="font-semibold text-gray-800 mb-2">Evidence-Based</h4>
                                <p className="text-gray-700">Access reliable mental health resources and proven support strategies.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
  