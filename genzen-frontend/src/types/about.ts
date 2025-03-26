export interface Feature {
  title: string;
  description: string;
}

export interface Mission {
  title: string;
  mission: string;
  description: string;
  audience: string[];
  features: Feature[];
}

export interface TeamMember {
  name: string;
  role: string;
  image: string;
  bio: string;
  links: {
    github?: string;
    linkedin?: string;
    portfolio?: string;
  };
}

export interface Team {
  team: TeamMember[];
}

export interface Privacy {
  title: string;
  lastUpdated: string;
  sections: {
    title: string;
    content: string;
  }[];
} 