/**
 * Morpheus v2 Knowledge Graph API Service
 */
import { api } from '../lib/api'

const v2 = api.create({ baseURL: '/api/v2' })

// ── Types ──

export interface Volume {
  id: string; project_id: string; volume_number: number
  title: string; summary: string; goal: string
  status: string; is_locked: boolean; sort_order: number
  created_at: string; updated_at: string
}

export interface StoryEvent {
  id: string; project_id: string; volume_id: string
  storyline_id: string | null  // 多线叙事：所属故事线
  event_number: number; title: string; summary: string; goal: string
  status: string; is_locked: boolean; sort_order: number
  involved_character_ids: string[]
  created_at: string; updated_at: string
}

export type StorylineStatus = 'active' | 'completed' | 'paused'

export interface Storyline {
  id: string; project_id: string; volume_id: string
  title: string; color: string; description: string
  status: StorylineStatus; sort_order: number
  created_at: string; updated_at: string
}

export type CharacterRole = 'protagonist' | 'supporting' | 'minion' | 'villain' | 'other'

export interface CharacterTemplate {
  id: string; project_id: string; name: string
  role_type: CharacterRole
  gender: string; identity: string; personality: string
  appearance: string; background: string; motivation: string
  is_alive: boolean
  created_at: string; updated_at: string
}

export interface CharacterState {
  id: string; character_id: string; age: string; status: string; location: string
  abilities: string[]; weapons: string[]; inventory: string[]
  emotional_state: string; battle_power: string
  custom_fields: Record<string, unknown>; as_of_chapter: number; updated_at: string
}

export interface CharacterRelation {
  id: string; project_id: string; character_a_id: string; character_b_id: string
  relation_type: string; strength: number; description: string
  turning_point: string; as_of_chapter: number; updated_at: string
}

export interface CheatSystem {
  id: string; project_id: string; name: string; core_logic: string
  limitations: string; upgrade_conditions: string; created_at: string; updated_at: string
}

export interface CheatState {
  id: string; cheat_id: string; current_level: string
  unlocked_features: string[]; usage_status: Record<string, unknown>
  custom_fields: Record<string, unknown>; as_of_chapter: number; updated_at: string
}

export interface WorldFact {
  id: string; project_id: string; category: string; title: string; content: string
  created_at: string; updated_at: string
}

export interface Foreshadowing {
  id: string; project_id: string; planted_chapter: number; description: string
  status: string; collected_chapter: number | null; collection_description: string
  created_at: string; updated_at: string
}

export interface OpenThread {
  id: string; project_id: string; title: string; description: string
  priority: string; opened_chapter: number; closed_chapter: number | null
  status: string; created_at: string; updated_at: string
}

export interface ConsistencyRule {
  id: string; project_id: string; rule_type: string; target: string; condition: string
  is_active: boolean; created_at: string; updated_at: string
}

export interface KnowledgeSummary {
  volumes: number; events: number; characters: number; relations: number
  cheats: number; world_facts: number
  foreshadowings_planted: number; foreshadowings_collected: number
  threads_open: number; rules: number
}

// ── Volumes ──

export const volumes = {
  list: (pid: string) => v2.get<Volume[]>(`/projects/${pid}/volumes`).then(r => r.data),
  create: (pid: string, data: Partial<Volume>) => v2.post<Volume>(`/projects/${pid}/volumes`, data).then(r => r.data),
  update: (pid: string, id: string, data: Partial<Volume>) => v2.put<Volume>(`/projects/${pid}/volumes/${id}`, data).then(r => r.data),
}

// ── Events ──

export const events = {
  list: (pid: string, volumeId?: string) =>
    v2.get<StoryEvent[]>(`/projects/${pid}/events`, { params: volumeId ? { volume_id: volumeId } : {} }).then(r => r.data),
  create: (pid: string, data: Partial<StoryEvent>) => v2.post<StoryEvent>(`/projects/${pid}/events`, data).then(r => r.data),
  update: (pid: string, id: string, data: Partial<StoryEvent>) => v2.put<StoryEvent>(`/projects/${pid}/events/${id}`, data).then(r => r.data),
}

// ── Storylines（多线叙事） ──

export const storylines = {
  list: (pid: string, volumeId?: string) =>
    v2.get<Storyline[]>(`/projects/${pid}/storylines`, { params: volumeId ? { volume_id: volumeId } : {} }).then(r => r.data),
  create: (pid: string, data: Partial<Storyline>) => v2.post<Storyline>(`/projects/${pid}/storylines`, data).then(r => r.data),
  update: (pid: string, id: string, data: Partial<Storyline>) => v2.put<Storyline>(`/projects/${pid}/storylines/${id}`, data).then(r => r.data),
  delete: (pid: string, id: string) => v2.delete(`/projects/${pid}/storylines/${id}`).then(r => r.data),
}

// ── Characters ──

export const characters = {
  list: (pid: string) => v2.get<CharacterTemplate[]>(`/projects/${pid}/characters`).then(r => r.data),
  create: (pid: string, data: Partial<CharacterTemplate>) => v2.post<CharacterTemplate>(`/projects/${pid}/characters`, data).then(r => r.data),
  update: (pid: string, id: string, data: Partial<CharacterTemplate>) => v2.put<CharacterTemplate>(`/projects/${pid}/characters/${id}`, data).then(r => r.data),
  getState: (pid: string, id: string) => v2.get<CharacterState>(`/projects/${pid}/characters/${id}/state`).then(r => r.data),
  upsertState: (pid: string, id: string, data: Partial<CharacterState>) =>
    v2.put<CharacterState>(`/projects/${pid}/characters/${id}/state`, data).then(r => r.data),
}

// ── Relations ──

export const relations = {
  list: (pid: string) => v2.get<CharacterRelation[]>(`/projects/${pid}/relations`).then(r => r.data),
  create: (pid: string, data: Partial<CharacterRelation>) => v2.post<CharacterRelation>(`/projects/${pid}/relations`, data).then(r => r.data),
  update: (pid: string, id: string, data: Partial<CharacterRelation>) => v2.put<CharacterRelation>(`/projects/${pid}/relations/${id}`, data).then(r => r.data),
}

// ── Cheats ──

export const cheats = {
  list: (pid: string) => v2.get<CheatSystem[]>(`/projects/${pid}/cheats`).then(r => r.data),
  create: (pid: string, data: Partial<CheatSystem>) => v2.post<CheatSystem>(`/projects/${pid}/cheats`, data).then(r => r.data),
  getState: (pid: string, id: string) => v2.get<CheatState>(`/projects/${pid}/cheats/${id}/state`).then(r => r.data),
  upsertState: (pid: string, id: string, data: Partial<CheatState>) =>
    v2.put<CheatState>(`/projects/${pid}/cheats/${id}/state`, data).then(r => r.data),
}

// ── World Facts ──

export const worldFacts = {
  list: (pid: string, category?: string) =>
    v2.get<WorldFact[]>(`/projects/${pid}/world-facts`, { params: category ? { category } : {} }).then(r => r.data),
  create: (pid: string, data: Partial<WorldFact>) => v2.post<WorldFact>(`/projects/${pid}/world-facts`, data).then(r => r.data),
  update: (pid: string, id: string, data: Partial<WorldFact>) => v2.put<WorldFact>(`/projects/${pid}/world-facts/${id}`, data).then(r => r.data),
  delete: (pid: string, id: string) => v2.delete(`/projects/${pid}/world-facts/${id}`).then(r => r.data),
}

// ── Foreshadowings ──

export const foreshadowings = {
  list: (pid: string, status?: string) =>
    v2.get<Foreshadowing[]>(`/projects/${pid}/foreshadowings`, { params: status ? { status } : {} }).then(r => r.data),
  create: (pid: string, data: Partial<Foreshadowing>) => v2.post<Foreshadowing>(`/projects/${pid}/foreshadowings`, data).then(r => r.data),
  update: (pid: string, id: string, data: Partial<Foreshadowing>) => v2.put<Foreshadowing>(`/projects/${pid}/foreshadowings/${id}`, data).then(r => r.data),
}

// ── Open Threads ──

export const threads = {
  list: (pid: string, status?: string) =>
    v2.get<OpenThread[]>(`/projects/${pid}/threads`, { params: status ? { status } : {} }).then(r => r.data),
  create: (pid: string, data: Partial<OpenThread>) => v2.post<OpenThread>(`/projects/${pid}/threads`, data).then(r => r.data),
  update: (pid: string, id: string, data: Partial<OpenThread>) => v2.put<OpenThread>(`/projects/${pid}/threads/${id}`, data).then(r => r.data),
}

// ── Consistency Rules ──

export const rules = {
  list: (pid: string) => v2.get<ConsistencyRule[]>(`/projects/${pid}/rules`).then(r => r.data),
  create: (pid: string, data: Partial<ConsistencyRule>) => v2.post<ConsistencyRule>(`/projects/${pid}/rules`, data).then(r => r.data),
  toggle: (pid: string, id: string, isActive: boolean) =>
    v2.patch(`/projects/${pid}/rules/${id}/toggle`, { is_active: isActive }).then(r => r.data),
}

// ── Summary ──

export const summary = (pid: string) => v2.get<KnowledgeSummary>(`/projects/${pid}/knowledge-summary`).then(r => r.data)
