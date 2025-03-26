export default function Footer() {
    return (
      <footer className="bg-white border-t py-4">
        <div className="container mx-auto text-center text-sm text-gray-600">
          © {new Date().getFullYear()} GenZen. All rights reserved.
        </div>
      </footer>
    );
  }
  