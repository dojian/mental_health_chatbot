import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import { Mission, Team, Privacy } from '@/types/about';

const contentDirectory = path.join(process.cwd(), 'src/content/about');
const privacyDirectory = path.join(process.cwd(), 'src/content/privacy');

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