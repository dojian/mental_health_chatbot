import Image from 'next/image';
import Link from 'next/link';
import { getMissionContent, getTeamContent } from '@/utils/content';
import { FaGithub, FaLinkedin, FaGlobe } from 'react-icons/fa';

export default async function About() {
    const mission = getMissionContent();
    const { team } = getTeamContent();
    // const { helpers } = getAcknowledgementContent();
    return (
        <>
            {/* Mission Section */}
            <section className="mb-12">
                <h1 className="text-2xl sm:text-3xl font-semibold mb-6 text-gray-800">{mission.title}</h1>
                <div className="bg-white/80 rounded-lg p-6 shadow-lg space-y-6">
                    <p className="text-lg text-gray-700">{mission.mission}</p>
                    <p className="text-lg text-gray-700">{mission.description}</p>
                    
                    {/* Supported Topics */}
                    <div className="mt-8">
                        <h2 className="text-xl font-semibold mb-4 text-gray-800">Topics We Support</h2>
                        <p className="text-gray-700 mb-4">{mission.supported_topics}</p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                            {mission.supported_topics_list.map((topic: string, index: number) => (
                                <div 
                                    key={index} 
                                    className="bg-white/50 p-3 rounded-lg text-gray-700 text-center hover:bg-white/80 transition-colors"
                                >
                                    {topic}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Features */}
                    <div className="mt-8">
                        <h2 className="text-xl font-semibold mb-4 text-gray-800">Our Features</h2>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {mission.features.map((feature, index) => (
                                <div key={index} className="bg-white/50 p-4 rounded-lg">
                                    <h3 className="font-semibold text-gray-800 mb-2">{feature.title}</h3>
                                    <p className="text-gray-700">{feature.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Disclaimer */}
                    <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <h2 className="text-xl font-semibold mb-4 text-gray-800">Important Disclaimer</h2>
                        <div className="text-gray-700 space-y-4 whitespace-pre-line">
                            {mission.disclaimer}
                        </div>
                    </div>
                </div>
            </section>

            {/* Team Section */}
            <section>
                <h2 className="text-2xl font-semibold mb-6 text-gray-800">Meet Our Team</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {team.map((member, index) => (
                        <div key={index} className="bg-white/80 rounded-lg p-6 shadow-lg">
                            <div className="aspect-square relative mb-4 rounded-lg overflow-hidden">
                                <Image
                                    src={member.image}
                                    alt={member.name}
                                    fill
                                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                                    className="object-cover"
                                    loading="lazy"
                                    quality={75}
                                    placeholder="blur"
                                    blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDABQODxIPDRQSEBIXFRQdHx4eHRseHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/2wBDAR0XFx4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                                />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-800">{member.name}</h3>
                            <p className="text-gray-600 mb-4">{member.role}</p>
                            <p className="text-gray-700 mb-4">{member.bio}</p>
                            <div className="flex space-x-4">
                                {member.links.github && (
                                    <Link href={member.links.github} target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900">
                                        <FaGithub className="w-6 h-6" />
                                    </Link>
                                )}
                                {member.links.linkedin && (
                                    <Link href={member.links.linkedin} target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900">
                                        <FaLinkedin className="w-6 h-6" />
                                    </Link>
                                )}
                                {member.links.portfolio && (
                                    <Link href={member.links.portfolio} target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900">
                                        <FaGlobe className="w-6 h-6" />
                                    </Link>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
                <br />
            </section>

            {/* Acknowledgements Section */}
            <section>
                <h2 className="text-2xl font-semibold mb-6 text-gray-800">Acknowledgements</h2>
                <div className="bg-white/80 rounded-lg p-6 shadow-lg space-y-6">
                    <div className="text-gray-700">
                        <p className="mb-4">
                            We would like to acknowledge the following mental health professionals who gave feedback and helped develop the mental-wellness resources.
                        </p>
                        <ul className="list-disc pl-6 space-y-2">
                            <li>Nikkolson Ang (M.S.) - Associate Marriage and Family Therapist</li>
                            <li>Cassandra Aguirre (M.A.) - School Psychologist</li>
                        </ul>
                    </div>
                </div>
            </section>
        </>
    );
}