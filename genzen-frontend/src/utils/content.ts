import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import { Mission, Team, Privacy } from '@/types/about';
import { Home } from '@/types/home';

const contentDirectory = path.join(process.cwd(), 'src/content_data/about');
const privacyDirectory = path.join(process.cwd(), 'src/content_data/privacy');
const homeDirectory = path.join(process.cwd(), 'src/content_data/home_data');

export function getMissionContent(): Mission {
  const fullPath = path.join(contentDirectory, 'mission.yaml');
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const content = yaml.load(fileContents) as Mission;
  return content;
}

export function getTeamContent(): Team {
  const fullPath = path.join(contentDirectory, 'team.yaml');
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const content = yaml.load(fileContents) as Team;
  return content;
}

export function getPrivacyContent(): Privacy {
  const fullPath = path.join(privacyDirectory, 'privacy.yaml');
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const content = yaml.load(fileContents) as Privacy;
  return content;
} 

export function getHomeContent(): Home {
  const fullPath = path.join(homeDirectory, 'home_data.yaml');
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const content = yaml.load(fileContents) as Home;
  return content;
}