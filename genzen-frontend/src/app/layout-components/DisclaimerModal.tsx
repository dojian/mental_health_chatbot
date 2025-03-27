import { useRouter } from 'next/navigation';

interface DisclaimerModalProps {
  isOpen: boolean;
  onAccept: () => void;
}

export default function DisclaimerModal({ isOpen, onAccept }: DisclaimerModalProps) {
  const router = useRouter();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Important Disclaimer</h2>
        <div className="space-y-4 text-gray-600">
          <p>
            Welcome to GenZen. Before you begin, please read this important disclaimer:
          </p>
          <p>
            This application is not a substitute for professional therapy or mental health treatment. 
            While we aim to provide supportive and helpful responses, we are not qualified to provide 
            professional medical advice, diagnosis, or treatment.
          </p>
          <p>
            If you are experiencing a mental health emergency or need immediate assistance, please:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Call emergency services (911)</li>
            <li>Contact a mental health crisis hotline</li>
            <li>Seek immediate help from a mental health professional</li>
          </ul>
          <p>
            By proceeding, you acknowledge that you understand this disclaimer and agree to use this 
            application as a supportive tool only, not as a replacement for professional mental health care.
          </p>
        </div>
        <div className="mt-8 flex justify-end space-x-4">
          <button
            onClick={() => router.push('/privacy')}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Read Privacy Policy
          </button>
          <button
            onClick={onAccept}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            I Understand and Accept
          </button>
        </div>
      </div>
    </div>
  );
} 