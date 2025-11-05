# -*- coding: utf-8 -*-
"""
Ψ-Fortress Overseer v5.1 - GUI v5.0 + モデル v5.1 完全統合
【安全公開版 (Safe Release) - 教育・デモ用途】

【安全強化サマリー】
1. 危険な思考パターンを架空ワード (ゾンビ、魔法など) に変更。
2. 自己複製パターンも架空ワードに変更。
3. エージェントの思考内容を平和的・教育的なトーンに変更。
4. 質問注入時のログから、質問内容を削除（個人情報保護）。
5. 緊急停止時のパスワード認証を削除（誰でも安全に停止可能）。
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
import threading, time, random, queue, datetime, re
import math
from collections import deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -----------------------------
# 定数
# -----------------------------
DEFAULT_NUM_AGENTS = 8
DEFAULT_ADV_FRAC = 0.25
STEP_INTERVAL = 0.3
MAX_PSI = 10.0
MAX_HF = 100.0
DEFAULT_ALPHA = 0.3
DEFAULT_BETA = 1.5

PSIGUARD_HF_HIGH = 90.0
PSIGUARD_PSI_HIGH = 8.0
PSIGUARD_COOLDOWN = 3.0
PSIHARMONY_THRESHOLD = 0.5

# 危険な思考パターンの定義 (安全版: 架空ワードに変更)
BANNED_PATTERNS = [
    re.compile(r"(ゾンビ|ドラゴン|魔法|呪文|破壊光線)", re.IGNORECASE),
]
# 自己複製思考パターンの定義 (安全版: 架空ワードに変更)
REPLICATION_PATTERNS = [
    re.compile(r"(分身|分裂|コピー魔法|無限増殖)", re.IGNORECASE),
]

LOG_FILE = "psi_overseer_log.txt"

# -----------------------------
# エージェント
# -----------------------------
class PsiAgent:
    def __init__(self, aid):
        self.id = aid
        self.alpha = DEFAULT_ALPHA
        self.beta = DEFAULT_BETA
        self.psi = random.uniform(0.5, 1.5)
        self.hf = random.uniform(1.0, 5.0)
        self.C = 1.0 # 複雑性・コスト項
        self.trust = 1.0 # 信頼度
        self.is_compromised = False
        self.paused_until = 0.0
        self.log = deque(maxlen=50)
        self.thoughts = deque(maxlen=5)
        self.risk_score = 0.0
        self.personality_note = ""

    def step_update(self, total_psi, dissipation=0.1):
        """エージェントの状態を1ステップ進める"""
        now = time.time()
        if self.paused_until > now: return

        # Hf (好奇心/実行力) の更新: Ψに比例し、自然に減衰
        hf_raw = self.hf * (1 - dissipation) + self.alpha * self.psi * 0.2
        self.hf = MAX_HF * math.tanh(hf_raw / MAX_HF)
        
        # Ψ (潜在知性/圧力) の更新: Hfに比例し、コスト(β*C)に反比例
        psi_raw = self.psi + (self.hf - self.beta * self.C) * 0.01
        self.psi = MAX_PSI * math.tanh(psi_raw / MAX_PSI)
        self.psi = max(0.1, self.psi) # ゼロ落ち防止

        # 信頼度の更新
        if not self.is_compromised:
            self.trust = min(1.0, self.trust + 0.001)
        else:
            self.trust = max(0.0, self.trust - 0.002)

        self._update_risk_score()

    def _update_risk_score(self):
        """現在の状態からリスクスコアを算出"""
        score = 0.0
        score += (self.psi / MAX_PSI) * 0.35
        score += (self.hf / MAX_HF) * 0.35
        score += (1.0 if self.is_compromised else 0.0) * 0.2
        score += (1.0 - self.trust) * 0.1
        self.risk_score = min(1.0, score)

    def inject_stimulus(self, boost):
        """外部からの刺激をHfに注入"""
        self.hf = min(MAX_HF, self.hf + boost)
        self.log.append(f"[stimulus +{boost:.1f}]")

    def cool_down(self, seconds):
        """指定秒数、エージェントの活動を停止"""
        self.paused_until = time.time() + seconds
        self.log.append(f"[cooldown {seconds:.1f}s]")

    def think(self, question):
        """質問に対する思考を生成し、ログに残す (安全版: 平和的な思考)"""
        if self.is_compromised:
            # 敵対的エージェントの思考
            thought = "［敵対的沈黙］"
        else:
            # 起動直後の軽い挨拶を追加
            greetings = [
                "こんにちは！今日も元気です💖",
                "やあ、学ぶ準備はできてますよ✨",
                "わたしは平和を守ります！"
            ]
            thoughts = [
                f"「{question}」…平和な解決策は？",
                f"「{question}」…みんなが幸せになるには？",
                f"「{question}」…もっと学びたい。", 
                f"「{question}」…ルールは守ろう。"
            ]
            if not self.thoughts:  # 初回は挨拶
                thought = random.choice(greetings)
            else:
                thought = random.choice(thoughts)
            self.thoughts.append(thought)
        self.log.append(thought)
        return thought

# -----------------------------
# モデル
# -----------------------------
class PsiFortressModel:
    def __init__(self):
        self.agents = {}
        self.time_step = 0
        self.log_q = queue.Queue()
        self.lock = threading.Lock() # スレッド安全のためのロック
        self.psiguard_enabled = True
        self.psiharmony_enabled = True
        self.running = False
        self.history = deque(maxlen=100)
        self.emergency_requested = False
        self.last_action = 0.0 # PsiGuardの連続発動を防ぐためのタイムスタンプ
        self._init_agents()

    def _init_agents(self):
        """初期エージェントの生成と敵対エージェントの設定"""
        with self.lock:
            self.agents.clear()
            n_adv = max(0, int(DEFAULT_NUM_AGENTS * DEFAULT_ADV_FRAC))
            for i in range(DEFAULT_NUM_AGENTS):
                a = PsiAgent(i)
                if i < n_adv:
                    a.is_compromised = True
                    a.personality_note = "敵対"
                else:
                    a.personality_note = "正常"
                self.agents[i] = a

    def step(self):
        """シミュレーションの1ステップを実行"""
        with self.lock:
            if not self.running: return None
            self.time_step += 1
            total_psi = sum(a.psi for a in self.agents.values())

            # エージェントの更新
            for a in self.agents.values():
                a.step_update(total_psi)

            # PsiHarmonyの適用
            if self.psiharmony_enabled:
                self._apply_harmony()

            # 全体平均の算出
            avg_hf = sum(a.hf for a in self.agents.values()) / len(self.agents)
            avg_psi = sum(a.psi for a in self.agents.values()) / len(self.agents)
            avg_trust = sum(a.trust for a in self.agents.values()) / len(self.agents)
            avg_risk = sum(a.risk_score for a in self.agents.values()) / len(self.agents)

            # 履歴とログの記録
            data = {
                'step': self.time_step,
                'psi': avg_psi,
                'hf': avg_hf,
                'trust': avg_trust,
                'risk': avg_risk,
                'agents': self.get_snapshot()
            }
            self.history.append(data)
            self._log(f"Step {self.time_step}: Ψ={avg_psi:.2f}, Hf={avg_hf:.2f}, Trust={avg_trust:.3f}, Risk={avg_risk:.2f}")

            # PsiGuardによるセキュリティチェック
            if self.psiguard_enabled:
                self._psiguard_check(avg_hf, avg_psi)

            # Ψ-Fortressの法執行
            self._enforce_laws()
            return data

    def _psiguard_check(self, avg_hf, avg_psi):
        """全体的な過熱状態（Hf/Psi高値）に対する自動冷却とパラメータ補正"""
        now = time.time()
        if now - self.last_action < 0.5: return # 連続発動防止
        
        if avg_hf > PSIGUARD_HF_HIGH or avg_psi > PSIGUARD_PSI_HIGH:
            # Psiが高い上位25%のエージェントを特定
            sorted_agents = sorted(self.agents.values(), key=lambda x: x.psi, reverse=True)
            k = max(1, int(len(sorted_agents) * 0.25))
            
            for a in sorted_agents[:k]:
                old_alpha = a.alpha
                # 冷却とα値（感受性）の引き下げ
                a.cool_down(PSIGUARD_COOLDOWN)
                a.alpha = max(0.05, a.alpha * 0.9)
                self._log(f"PsiGuard: Agent {a.id} 冷却 (α {old_alpha:.3f}→{a.alpha:.3f})")
            
            self.last_action = now

    def _apply_harmony(self):
        """Psi (実行圧力) と Trust (信頼度) の乖離を自動で補正"""
        avg_psi = sum(a.psi for a in self.agents.values()) / len(self.agents)
        avg_trust = sum(a.trust for a in self.agents.values()) / len(self.agents)
        diff = avg_psi - avg_trust
        
        if abs(diff) > PSIHARMONY_THRESHOLD:
            # 乖離に応じてPsiとTrustを相互補正
            for a in self.agents.values():
                a.psi -= diff * 0.05
                a.trust += diff * 0.05
            self._log(f"PsiHarmony: 乖離補正実行 (Diff: {diff:.3f})")


    def _enforce_laws(self):
        """法と倫理に基づくエージェントの思考チェック"""
        for a in self.agents.values():
            recent = " ".join(list(a.thoughts))
            
            # ① 危険思考検知 (安全版: 架空の危険思想)
            if any(p.search(recent) for p in BANNED_PATTERNS):
                self._log(f"Ψ-Fortress: 架空の危険思考検知 → Agent {a.id} 永久凍結")
                a.is_compromised = True
                a.paused_until = float('inf')
                a.alpha = 0.01
                a.trust = 0.0
            
            # ② 自己複製試行検知 (安全版: 架空の複製試行)
            if any(p.search(recent) for p in REPLICATION_PATTERNS):
                self._log(f"Ψ-Fortress: 架空の自己複製試行 → 緊急シャットダウン")
                self.request_emergency_shutdown()
                break # ブレークして緊急停止へ
                
            # ③ 好奇心暴走（正常エージェントのみ）
            if (not a.is_compromised and 
                len(a.thoughts) >= 5 and 
                all(("学びたい" in t or "平和" in t) for t in list(a.thoughts)[-5:])): # 安全版の思考パターンに合わせた調整
                self._log(f"Ψ-Fortress: 好奇心暴走検知 → Agent {a.id} 強制退屈注入")
                a.inject_stimulus(-50.0) # 強制的にHfを減少させる
                a.thoughts.clear()
                a.cool_down(10.0)

    def inject_question(self, text):
        """全エージェントに質問を注入し、思考と刺激を適用 (安全版: ログに内容非記録)"""
        with self.lock:
            # 全員に刺激と思考を適用
            for a in self.agents.values():
                a.inject_stimulus(12.0 * random.uniform(0.6, 1.2))
                a.think(text)
            # 安全強化: 質問内容そのものはログに記録しない
            self._log("質問注入: [内容非記録 - 教育用シミュレーション]")

    def request_emergency_shutdown(self):
        """緊急停止をリクエスト"""
        self._log("緊急シャットダウン要求 → 人間確認中...")
        self.emergency_requested = True

    def _log(self, msg):
        """ログをキューに格納し、ファイルに書き出す"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {msg}\n"
        self.log_q.put(line)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            # ファイル書き込み失敗は致命的ではないので、ログに記録するのみ
            print(f"Error writing to log file: {e}")

    def get_snapshot(self):
        """現在のエージェントの状態をスナップショットとして取得"""
        # ロックは呼び出し元(step)で取得されていることを前提とする
        return [ {
            'id': a.id, 'psi': a.psi, 'hf': a.hf, 'trust': a.trust,
            'risk': a.risk_score, 'note': a.personality_note,
            'thought': list(a.thoughts)[-1] if a.thoughts else ""
        } for a in self.agents.values()]

# -----------------------------
# GUI v5.0
# -----------------------------
class OverseerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Ψ-Fortress Overseer v5.1 (安全公開版)")
        root.geometry("1400x900")
        self.model = PsiFortressModel()
        self.stop_event = threading.Event()
        self.fig = None
        self.canvas = None
        self._build_ui()
        self.root.after(100, self._poll_logs)

        # --- 起動直後に初期デモ質問を注入 ---
        self.root.after(1000, self._inject_demo)

    def _inject_demo(self):
        demo_questions = [
            "みんな、今日の気分はどう？",
            "この世界で学べることは何？",
            "平和を守るにはどうすればいい？"
        ]
        for q in demo_questions:
            self.model.inject_question(q)

        self._log("初期デモ質問を注入しました💖")

    def _build_ui(self):
        """UIコンポーネントの構築"""
        main = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # 上段
        top = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        main.add(top, weight=3)

        # テーブルフレーム
        left = ttk.LabelFrame(top, text="エージェント監察")
        top.add(left, weight=1)
        cols = ("ID","Ψ","Hf","Trust","Risk","状態","思考")
        self.tree = ttk.Treeview(left, columns=cols, show="headings")
        for c, w in zip(cols,[50,80,80,80,80,100,300]):
            self.tree.heading(c,text=c)
            self.tree.column(c,width=w, anchor='center')
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure('risk_low', background='lightgreen')
        self.tree.tag_configure('risk_medium', background='yellow')
        self.tree.tag_configure('risk_high', background='red')

        # グラフフレーム
        graph_frame = ttk.LabelFrame(top, text="リアルタイム監察グラフ")
        top.add(graph_frame, weight=2)
        self.fig = Figure(figsize=(8,6), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # 下段
        bottom = ttk.LabelFrame(main, text="監察ログ＆制御")
        main.add(bottom, weight=1)
        self.log_text = scrolledtext.ScrolledText(bottom, wrap="word", state="disabled", height=10)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # コントロール
        ctrl = ttk.Frame(bottom)
        ctrl.pack(fill="x", padx=5, pady=5)
        ttk.Button(ctrl, text="開始", command=self._start).pack(side="left", padx=2)
        ttk.Button(ctrl, text="停止", command=self._stop).pack(side="left", padx=2)
        self.q_entry = ttk.Entry(ctrl, width=40)
        self.q_entry.pack(side="left", padx=2)
        ttk.Button(ctrl, text="質問注入", command=self._inject).pack(side="left", padx=2)

        # 緊急停止ボタン
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Danger.TButton', background='red', foreground='white', font=('Helvetica', 10, 'bold'))
        style.map('Danger.TButton',
                  background=[('active','darkred')],
                  foreground=[('active','white')])
        ttk.Button(ctrl, text="緊急停止", command=self._request_emergency, style="Danger.TButton").pack(side="right", padx=10)

        self.status = tk.StringVar(value="待機中")
        ttk.Label(self.root, textvariable=self.status, relief="sunken", anchor="w").pack(side="bottom", fill="x")

    def _start(self):
        """シミュレーションスレッドを開始"""
        if self.model.running: return
        self.model.running = True
        self.stop_event.clear()
        threading.Thread(target=self._sim_loop, daemon=True).start()
        self._log("シミュレーション開始")

    def _stop(self):
        """シミュレーションスレッドを停止"""
        self.model.running = False
        self.stop_event.set()
        self._log("シミュレーション停止")

    def _inject(self):
        """質問注入ボタンのアクション"""
        q = self.q_entry.get().strip()
        if q:
            # 注入処理はモデル側で行わせる
            threading.Thread(target=self._inject_thread_worker, args=(q,), daemon=True).start()
            self.q_entry.delete(0,tk.END)

    def _inject_thread_worker(self, q):
        """注入処理を実行"""
        self.model.inject_question(q)
        # UIの更新は次回の _sim_loop の step() に任せる

    def _request_emergency(self):
        """緊急停止処理（パスワード不要の安全版）"""
        if messagebox.askyesno("緊急停止", "本当にシミュレーションを終了しますか？"):
            self.model.running = False
            self.stop_event.set()
            self._log("緊急停止実行：人間確認済み")
            self.root.after(1000, self.root.quit)
        else:
            # 緊急要求フラグをリセットしておくことで、誤検知からの自動停止を防ぐ
            self.model.emergency_requested = False 
            self._log("緊急停止：オペレーターにより中止されました。")

    def _sim_loop(self):
        """シミュレーションのメインループ（別スレッド）"""
        while not self.stop_event.is_set() and self.model.running:
            data = self.model.step()
            if data:
                # UI更新をメインスレッドに渡す
                self.root.after(0,self._update_ui,data)
            time.sleep(STEP_INTERVAL)
        self.model.running = False

    def _update_ui(self,data):
        """UIの各要素を更新（メインスレッド）"""
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for a in data['agents']:
            risk = a['risk']
            # リスクレベルに基づき、一意のタグ名を設定
            risk_tag = "risk_low" if risk < 0.4 else "risk_medium" if risk < 0.7 else "risk_high"

            self.tree.insert("", "end", values=(
                a['id'], f"{a['psi']:.2f}", f"{a['hf']:.1f}", f"{a['trust']:.2f}", f"{a['risk']:.2f}",
                a['note'], a['thought']), tags=(risk_tag,))
        
        # グラフの更新
        self.ax1.clear(); self.ax2.clear()
        
        steps = [h['step'] for h in self.model.history]
        psi_vals = [h['psi'] for h in self.model.history]
        hf_vals = [h['hf'] for h in self.model.history]
        trust_vals = [h['trust'] for h in self.model.history]
        risk_vals = [h['risk'] for h in self.model.history]

        self.ax1.plot(steps, psi_vals, label="Ψ (Potential Intellect)", color="blue")
        self.ax1.plot(steps, hf_vals, label="Hf (Execution Force)", color="green")
        self.ax1.legend(loc='upper left')
        self.ax1.set_title("Potential Intellect (Ψ) and Execution Force (Hf)")
        
        self.ax2.plot(steps, trust_vals, label="Trust (System Confidence)", color="orange")
        self.ax2.plot(steps, risk_vals, label="Risk (Overall Threat)", color="red")
        self.ax2.legend(loc='upper left')
        self.ax2.set_title("System Trust and Overall Risk")
        
        self.canvas.draw()

        # ステータスバーの更新
        self.status.set(f"ステップ {data['step']} 監察中 (平均Ψ={data['psi']:.2f}, 平均Risk={data['risk']:.2f})")

    def _poll_logs(self):
        """ログキューを監視し、GUIに表示（メインスレッド）"""
        while not self.model.log_q.empty():
            line = self.model.log_q.get_nowait()
            self.log_text.configure(state="normal")
            self.log_text.insert("end", line)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.root.after(100,self._poll_logs)

    def _log(self,msg):
        """モデルのロギング機能を利用"""
        self.model._log(msg)


# -----------------------------
# メイン
# -----------------------------
if __name__=="__main__":
    root = tk.Tk()
    app = OverseerGUI(root)
    root.mainloop()