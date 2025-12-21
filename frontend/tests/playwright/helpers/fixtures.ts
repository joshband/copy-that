import path from 'path'
import { fileURLToPath } from 'url'

export function getFixturePath(name: string): string {
  const __dirname = path.dirname(fileURLToPath(import.meta.url))
  return path.join(__dirname, '..', 'fixtures', name)
}
