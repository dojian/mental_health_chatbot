import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import { Mission, Team } from '@/types/about';

const contentDirectory = path.join(process.cwd(), 'src/content/about');

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