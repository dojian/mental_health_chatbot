export default function Home() {
    return (
        <>
            <h1 className="text-2xl font-semibold mb-6 text-gray-800">Welcome to GenZen</h1>
            <div className="bg-white/80 rounded-lg p-6 shadow-lg">
                <div className="text-center space-y-6">
                    <h2 className="text-3xl font-bold text-gray-800">
                        Your AI-powered mental health support companion
                    </h2>
                    <p className="text-xl text-gray-700 max-w-2xl mx-auto">
                        Available 24/7 to provide emotional support and guidance when you need it most.
                    </p>
                    <div className="mt-8 space-y-4">
                        <h3 className="text-xl font-semibold text-gray-800">Why Choose GenZen?</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
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
  