import { useEffect, useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import PageTransition from '../components/ui/PageTransition'
import Skeleton from '../components/ui/Skeleton'
import {
  volumes, events, characters, relations, cheats, worldFacts,
  foreshadowings, threads, rules, summary,
  type Volume, type StoryEvent, type CharacterTemplate,
  type CheatSystem, type WorldFact, type Foreshadowing,
  type OpenThread, type ConsistencyRule, type KnowledgeSummary,
} from '../services/knowledgeV2'
import { api } from '../lib/api'

const TABS = ['大纲', '角色', '金手指', '世界观', '伏笔/线索', '规则'] as const
type Tab = typeof TABS[number]

function useProjectId(): string {
  const { projectId } = useParams<{ projectId: string }>()
  return projectId!
}

/* ── Loading spinner ── */
function Spinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
    </div>
  )
}

/* ── Section wrapper ── */
function Section({ title, children, action }: { title: string; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-zinc-200 bg-white p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-zinc-800">{title}</h3>
        {action}
      </div>
      {children}
    </div>
  )
}

/* ── Simple inline form ── */
function InlineForm({ fields, onSubmit, placeholder }: {
  fields: { key: string; label: string; type?: string; placeholder?: string }[]
  onSubmit: (vals: Record<string, string>) => void
  placeholder?: string
}) {
  const [open, setOpen] = useState(false)
  const [vals, setVals] = useState<Record<string, string>>({})

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="text-xs text-indigo-600 hover:text-indigo-800">
        + {placeholder || '新增'}
      </button>
    )
  }

  return (
    <div className="flex flex-wrap gap-2 items-end">
      {fields.map(f => (
        <div key={f.key}>
          <label className="text-xs text-zinc-500 block mb-1">{f.label}</label>
          <input
            type={f.type || 'text'}
            placeholder={f.placeholder || f.label}
            value={vals[f.key] || ''}
            onChange={e => setVals(v => ({ ...v, [f.key]: e.target.value }))}
            className="border border-zinc-300 rounded px-2 py-1 text-sm w-32 focus:outline-none focus:border-indigo-400"
          />
        </div>
      ))}
      <button onClick={() => { onSubmit(vals); setVals({}); setOpen(false) }}
        className="px-3 py-1 bg-indigo-600 text-white text-xs rounded hover:bg-indigo-700">
        确定
      </button>
      <button onClick={() => { setOpen(false); setVals({}) }}
        className="px-3 py-1 text-zinc-500 text-xs hover:text-zinc-700">
        取消
      </button>
    </div>
  )
}

/* ═══════════════════════════════════
   Tab: 大纲 (Outline)
   ═══════════════════════════════════ */
function OutlineTab({ pid }: { pid: string }) {
  const [vols, setVols] = useState<Volume[]>([])
  const [evtMap, setEvtMap] = useState<Record<string, StoryEvent[]>>({})
  const [chapterMap, setChapterMap] = useState<Record<string, { chapter_number: number; title: string; status: string }[]>>({})
  const [expanded, setExpanded] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    const v = await volumes.list(pid)
    setVols(v)
    const allEvts = await events.list(pid)
    const m: Record<string, StoryEvent[]> = {}
    for (const e of allEvts) {
      ;(m[e.volume_id] ??= []).push(e)
    }
    setEvtMap(m)
    // Load chapters grouped by event_id
    try {
      const chRes = await api.get<{ id: string; chapter_number: number; title: string; status: string; event_id?: string }[]>(`/projects/${pid}/chapters`)
      const cm: Record<string, typeof chRes> = {}
      for (const c of chRes.data) {
        if (c.event_id) {
          ;(cm[c.event_id] ??= []).push(c)
        }
      }
      setChapterMap(cm)
    } catch { /* chapters API may not have event_id yet */ }
    setLoading(false)
  }, [pid])

  useEffect(() => { load() }, [load])

  const addVol = async (vals: Record<string, string>) => {
    await volumes.create(pid, {
      title: vals.title, volume_number: Number(vals.volume_number || vols.length + 1),
      summary: vals.summary || '', goal: vals.goal || '',
    })
    load()
  }

  const addEvt = async (volId: string, vals: Record<string, string>) => {
    await events.create(pid, {
      volume_id: volId, title: vals.title, event_number: Number(vals.event_number || (evtMap[volId]?.length || 0) + 1),
      summary: vals.summary || '', goal: vals.goal || '',
    })
    load()
  }

  if (loading) return <Skeleton className="h-64" />

  return (
    <div>
      <Section title="卷" action={
        <InlineForm fields={[{ key: 'title', label: '卷名', placeholder: '如：新手村' }]} onSubmit={addVol} placeholder="新增卷" />
      }>
        {vols.length === 0 && <p className="text-sm text-zinc-400">暂无卷，请先创建</p>}
        {vols.map(v => (
          <div key={v.id} className="mb-3">
            <div className="flex items-center gap-2 cursor-pointer group" onClick={() => setExpanded(expanded === v.id ? null : v.id)}>
              <span className="text-zinc-400 text-xs">{expanded === v.id ? '▼' : '▶'}</span>
              <span className="text-sm font-medium text-zinc-800 group-hover:text-indigo-600">{v.title}</span>
              {v.is_locked && <span className="text-xs bg-amber-100 text-amber-700 px-1 rounded">已锁定</span>}
              {v.summary && <span className="text-xs text-zinc-400 ml-2">{v.summary}</span>}
            </div>
            {expanded === v.id && (
              <div className="ml-6 mt-2 border-l-2 border-zinc-200 pl-3">
                {(evtMap[v.id] || []).map(e => (
                  <div key={e.id} className="py-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-zinc-500">📌</span>
                      <span className="text-sm text-zinc-700">{e.title}</span>
                      {e.summary && <span className="text-xs text-zinc-400">{e.summary}</span>}
                      <span className={`text-xs px-1 rounded ${e.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-zinc-100 text-zinc-500'}`}>
                      {e.status}
                    </span>
                    </div>
                    {(chapterMap[e.id] || []).length > 0 && (
                      <div className="ml-6 mt-1">
                        {(chapterMap[e.id] || []).map(ch => (
                          <div key={ch.id} className="text-xs text-zinc-400 py-0.5 flex items-center gap-1">
                            <span>📄 第{ch.chapter_number}章 {ch.title}</span>
                            <span className={`px-1 rounded ${ch.status === 'final' ? 'bg-blue-100 text-blue-600' : 'bg-zinc-100 text-zinc-400'}`}>
                              {ch.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                <div className="mt-2">
                  <InlineForm
                    fields={[{ key: 'title', label: '事件名', placeholder: '如：初入江湖' }]}
                    onSubmit={vals => addEvt(v.id, vals)}
                    placeholder="+ 新增事件"
                  />
                </div>
              </div>
            )}
          </div>
        ))}
      </Section>
    </div>
  )
}

/* ═══════════════════════════════════
   Tab: 角色 (Characters)
   ═══════════════════════════════════ */
function CharactersTab({ pid }: { pid: string }) {
  const [chars, setChars] = useState<CharacterTemplate[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    setChars(await characters.list(pid))
    setLoading(false)
  }, [pid])

  useEffect(() => { load() }, [load])

  const addChar = async (vals: Record<string, string>) => {
    await characters.create(pid, {
      name: vals.name, gender: vals.gender || '', identity: vals.identity || '',
      personality: vals.personality || '',
    })
    load()
  }

  if (loading) return <Skeleton className="h-64" />

  return (
    <Section title="角色列表" action={
      <InlineForm
        fields={[
          { key: 'name', label: '姓名' },
          { key: 'gender', label: '性别' },
          { key: 'identity', label: '身份' },
        ]}
        onSubmit={addChar}
        placeholder="+ 新增角色"
      />
    }>
      {chars.length === 0 && <p className="text-sm text-zinc-400">暂无角色</p>}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-zinc-500 border-b">
              <th className="pb-2 pr-3">姓名</th>
              <th className="pb-2 pr-3">性别</th>
              <th className="pb-2 pr-3">身份</th>
              <th className="pb-2 pr-3">性格</th>
              <th className="pb-2">状态</th>
            </tr>
          </thead>
          <tbody>
            {chars.map(c => (
              <tr key={c.id} className="border-b border-zinc-100">
                <td className="py-2 pr-3 font-medium">{c.name}</td>
                <td className="py-2 pr-3 text-zinc-500">{c.gender}</td>
                <td className="py-2 pr-3 text-zinc-500">{c.identity}</td>
                <td className="py-2 pr-3 text-zinc-500">{c.personality}</td>
                <td className="py-2">
                  <span className={`text-xs px-1 rounded ${c.is_alive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {c.is_alive ? '存活' : '死亡'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Section>
  )
}

/* ═══════════════════════════════════
   Tab: 金手指 (Cheat Systems)
   ═══════════════════════════════════ */
function CheatsTab({ pid }: { pid: string }) {
  const [cheatList, setCheatList] = useState<CheatSystem[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    setCheatList(await cheats.list(pid))
    setLoading(false)
  }, [pid])

  useEffect(() => { load() }, [load])

  const addCheat = async (vals: Record<string, string>) => {
    await cheats.create(pid, { name: vals.name, core_logic: vals.core_logic || '' })
    load()
  }

  if (loading) return <Skeleton className="h-64" />

  return (
    <Section title="金手指" action={
      <InlineForm fields={[{ key: 'name', label: '名称' }, { key: 'core_logic', label: '核心逻辑' }]} onSubmit={addCheat} />
    }>
      {cheatList.length === 0 && <p className="text-sm text-zinc-400">暂无金手指</p>}
      {cheatList.map(c => (
        <div key={c.id} className="mb-3 p-3 rounded border border-zinc-200">
          <h4 className="font-medium text-sm">{c.name}</h4>
          <p className="text-xs text-zinc-500 mt-1">核心逻辑：{c.core_logic}</p>
          {c.limitations && <p className="text-xs text-zinc-400 mt-1">限制：{c.limitations}</p>}
        </div>
      ))}
    </Section>
  )
}

/* ═══════════════════════════════════
   Tab: 世界观 (World Facts)
   ═══════════════════════════════════ */
function WorldTab({ pid }: { pid: string }) {
  const [facts, setFacts] = useState<WorldFact[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    setFacts(await worldFacts.list(pid))
    setLoading(false)
  }, [pid])

  useEffect(() => { load() }, [load])

  const addFact = async (vals: Record<string, string>) => {
    await worldFacts.create(pid, {
      category: vals.category || '设定', title: vals.title, content: vals.content,
    })
    load()
  }

  const deleteFact = async (id: string) => {
    await worldFacts.delete(pid, id)
    load()
  }

  if (loading) return <Skeleton className="h-64" />

  const categories = [...new Set(facts.map(f => f.category))]

  return (
    <div>
      <Section title="世界观设定" action={
        <InlineForm
          fields={[
            { key: 'title', label: '标题' },
            { key: 'category', label: '分类', placeholder: '如：设定' },
            { key: 'content', label: '内容' },
          ]}
          onSubmit={addFact}
        />
      }>
        {categories.map(cat => (
          <div key={cat} className="mb-4">
            <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wide mb-2">{cat}</h4>
            {facts.filter(f => f.category === cat).map(f => (
              <div key={f.id} className="flex items-start justify-between py-1">
                <div>
                  <span className="text-sm font-medium">{f.title}</span>
                  <p className="text-xs text-zinc-500">{f.content}</p>
                </div>
                <button onClick={() => deleteFact(f.id)} className="text-xs text-red-400 hover:text-red-600 ml-2">删除</button>
              </div>
            ))}
          </div>
        ))}
        {facts.length === 0 && <p className="text-sm text-zinc-400">暂无世界观设定</p>}
      </Section>
    </div>
  )
}

/* ═══════════════════════════════════
   Tab: 伏笔/线索 (Foreshadowings & Threads)
   ═══════════════════════════════════ */
function PlotThreadsTab({ pid }: { pid: string }) {
  const [fsList, setFsList] = useState<Foreshadowing[]>([])
  const [thList, setThList] = useState<OpenThread[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    const [fs, th] = await Promise.all([foreshadowings.list(pid), threads.list(pid)])
    setFsList(fs)
    setThList(th)
    setLoading(false)
  }, [pid])

  useEffect(() => { load() }, [load])

  const addFs = async (vals: Record<string, string>) => {
    await foreshadowings.create(pid, {
      planted_chapter: Number(vals.planted_chapter || 0), description: vals.description || '',
    })
    load()
  }

  const addTh = async (vals: Record<string, string>) => {
    await threads.create(pid, {
      title: vals.title || '', description: vals.description || '',
      opened_chapter: Number(vals.opened_chapter || 0),
    })
    load()
  }

  const collectFs = async (id: string) => {
    const chapter = prompt('在哪一章回收此伏笔？')
    if (chapter) {
      await foreshadowings.update(pid, id, { status: 'collected', collected_chapter: Number(chapter) })
      load()
    }
  }

  const closeTh = async (id: string) => {
    const chapter = prompt('在哪一章关闭此线索？')
    if (chapter) {
      await threads.update(pid, id, { status: 'closed', closed_chapter: Number(chapter) })
      load()
    }
  }

  if (loading) return <Skeleton className="h-64" />

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Section title={`伏笔 (${fsList.filter(f => f.status === 'planted').length} 未收)`} action={
        <InlineForm
          fields={[{ key: 'planted_chapter', label: '章', type: 'number' }, { key: 'description', label: '描述' }]}
          onSubmit={addFs}
        />
      }>
        {fsList.map(f => (
          <div key={f.id} className="py-1 flex items-center justify-between">
            <div>
              <span className={`text-xs px-1 rounded mr-1 ${f.status === 'planted' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}`}>
                {f.status === 'planted' ? '已埋' : '已收'}
              </span>
              <span className="text-sm">第{f.planted_chapter}章</span>
              <span className="text-sm text-zinc-600 ml-2">{f.description}</span>
            </div>
            {f.status === 'planted' && (
              <button onClick={() => collectFs(f.id)} className="text-xs text-indigo-500 hover:text-indigo-700">回收</button>
            )}
          </div>
        ))}
      </Section>

      <Section title={`线索 (${thList.filter(t => t.status === 'open').length} 未结)`} action={
        <InlineForm
          fields={[{ key: 'title', label: '标题' }, { key: 'opened_chapter', label: '起始章', type: 'number' }]}
          onSubmit={addTh}
        />
      }>
        {thList.map(t => (
          <div key={t.id} className="py-1 flex items-center justify-between">
            <div>
              <span className={`text-xs px-1 rounded mr-1 ${t.status === 'open' ? 'bg-blue-100 text-blue-700' : 'bg-zinc-100 text-zinc-500'}`}>
                {t.status === 'open' ? '开放' : '关闭'}
              </span>
              <span className="text-sm font-medium">{t.title}</span>
              <span className="text-xs text-zinc-400 ml-1">第{t.opened_chapter}章</span>
            </div>
            {t.status === 'open' && (
              <button onClick={() => closeTh(t.id)} className="text-xs text-indigo-500 hover:text-indigo-700">关闭</button>
            )}
          </div>
        ))}
      </Section>
    </div>
  )
}

/* ═══════════════════════════════════
   Tab: 规则 (Consistency Rules)
   ═══════════════════════════════════ */
function RulesTab({ pid }: { pid: string }) {
  const [ruleList, setRuleList] = useState<ConsistencyRule[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    setRuleList(await rules.list(pid))
    setLoading(false)
  }, [pid])

  useEffect(() => { load() }, [load])

  const addRule = async (vals: Record<string, string>) => {
    await rules.create(pid, {
      rule_type: vals.rule_type || '', target: vals.target || '', condition: vals.condition || '',
    })
    load()
  }

  if (loading) return <Skeleton className="h-64" />

  return (
    <Section title="一致性规则" action={
      <InlineForm
        fields={[
          { key: 'rule_type', label: '类型', placeholder: '如：角色死亡' },
          { key: 'target', label: '对象' },
          { key: 'condition', label: '条件' },
        ]}
        onSubmit={addRule}
      />
    }>
      {ruleList.length === 0 && <p className="text-sm text-zinc-400">暂无规则</p>}
      {ruleList.map(r => (
        <div key={r.id} className="flex items-center justify-between py-2 border-b border-zinc-100">
          <div>
            <span className="text-sm font-medium">{r.target}</span>
            <span className="text-xs text-zinc-400 ml-2">[{r.rule_type}]</span>
            <p className="text-xs text-zinc-500">{r.condition}</p>
          </div>
          <button
            onClick={() => rules.toggle(pid, r.id, !r.is_active).then(load)}
            className={`text-xs px-2 py-0.5 rounded ${r.is_active ? 'bg-green-100 text-green-700' : 'bg-zinc-100 text-zinc-400'}`}
          >
            {r.is_active ? '启用' : '禁用'}
          </button>
        </div>
      ))}
    </Section>
  )
}

/* ═══════════════════════════════════
   Main Page
   ═══════════════════════════════════ */
export default function KnowledgeGraphV2Page() {
  const pid = useProjectId()
  const [tab, setTab] = useState<Tab>('大纲')
  const [stats, setStats] = useState<KnowledgeSummary | null>(null)

  useEffect(() => {
    summary(pid).then(setStats).catch(() => {})
  }, [pid])

  const TabComponent: Record<Tab, React.FC<{ pid: string }>> = {
    '大纲': OutlineTab,
    '角色': CharactersTab,
    '金手指': CheatsTab,
    '世界观': WorldTab,
    '伏笔/线索': PlotThreadsTab,
    '规则': RulesTab,
  }

  const Comp = TabComponent[tab]

  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold text-zinc-900">知识图谱 v2</h1>
          {stats && (
            <div className="flex gap-3 text-xs text-zinc-500">
              <span>{stats.volumes} 卷</span>
              <span>{stats.events} 事件</span>
              <span>{stats.characters} 角色</span>
              <span>{stats.foreshadowings_planted} 伏笔</span>
              <span>{stats.threads_open} 线索</span>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 border-b border-zinc-200 mb-6">
          {TABS.map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                tab === t
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-zinc-500 hover:text-zinc-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <Comp pid={pid} />
      </div>
    </PageTransition>
  )
}
