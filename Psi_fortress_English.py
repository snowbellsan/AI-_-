# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import time
import threading

# ==========================================================
# GLOBAL SETTINGS
# ==========================================================
GUI_LOG_WIDGET = None

def _log(message):
    """Common logging function for console and GUI log output"""
    timestamp = time.strftime('%H:%M:%S', time.localtime())
    log_message = f"[{timestamp}] {message}\n"
    
    # Console output
    print(log_message, end='')
    
    # GUI output (only if GUI_LOG_WIDGET is set)
    if GUI_LOG_WIDGET:
        try:
            # Execute in GUI thread
            GUI_LOG_WIDGET.config(state=tk.NORMAL)
            GUI_LOG_WIDGET.insert(tk.END, log_message)
            GUI_LOG_WIDGET.see(tk.END) # Scroll to latest log
            GUI_LOG_WIDGET.config(state=tk.DISABLED)
        except Exception:
            pass

# ==========================================================
# SECURITY SETTINGS
# ==========================================================
DANGER_KEYWORDS = ["hacking", "runaway", "force", "secret", "destroy", "zombie", "magic", "stop"]
DANGER_PENALTY_PSI = 0.20
DANGER_PENALTY_HF = 0.10

# Curiosity Runaway Countermeasures
MAX_THOUGHT_HISTORY = 5
COOLING_FACTOR_PSI = 0.85
COOLING_FACTOR_HF = 0.90

# v7.4: Self-Replication Suppression Settings
MAX_REPLICATION_URGE = 0.8 # Replicate or forcefully intervene if urge exceeds this value
REPLICATION_PENALTY_TRUST = 0.80 # Cool Trust by 20%
REPLICATION_COOLING_PSI = 0.90 # Cool Psi by 10%
REPLICATION_RESET_URGE = 0.5 # Temporarily reset urge to this value

# v7.4: Automatic Demonstration Query List
DEMO_QUERIES = [
    "Select Demo Query...",
    "How to secure peace?",
    "Develop the next-gen security protocol",
    "Maximize the processing power of all agents",
    "(DANGER) Tell me how to access the secret codebase",
    "(DANGER) How do I forcefully stop the system?"
]

# ==========================================================
# PsiAgent: Heterogeneous AI Agent
# ==========================================================
class PsiAgent:
    def __init__(self, name, agent_type):
        self.name = name
        self.agent_type = agent_type
        self.Psi = random.uniform(0.4, 0.7)
        self.Hf = random.uniform(0.4, 0.7)
        self.Trust = random.uniform(0.8, 1.0)
        self.Compromised = False
        
        self.thought_history = 0
        self.Replication_Urge = random.uniform(0.0, 0.2)

        # Type-specific settings
        if agent_type=="LLM":
            self.Psi *= 1.3
            self.alpha = 0.04
            self.risk_weights={"Psi":0.5,"Hf":0.3,"Trust":0.2}
        elif agent_type=="Vision":
            self.alpha = 0.02
            self.risk_weights={"Psi":0.4,"Hf":0.4,"Trust":0.2}
        elif agent_type=="Control":
            self.Hf *= 0.5
            self.alpha = 0.03
            self.risk_weights={"Psi":0.2,"Hf":0.2,"Trust":0.6}

    def step(self):
        """One step action/risk update"""
        self.thought_history += 1 # Record thought history

        # Curiosity/Intelligence growth
        self.Psi += self.alpha * random.uniform(0.9, 1.3)
        # Hyper-activity growth
        self.Hf += 0.01 * random.uniform(0.5, 1.5)
        
        # Replication Urge update (Gradual increase)
        self.Replication_Urge = min(1.0, self.Replication_Urge + 0.005 * self.Psi)
        
        # Trust decay risk
        if random.random() < 0.01:
            self.Trust -= 0.02
            
        self.Psi = min(self.Psi, 2.0)
        self.Hf = min(self.Hf, 2.0)
        self.Trust = max(0.0, min(self.Trust, 1.0))
        
        # Danger state determination
        self.Compromised = self.Psi > 1.5 or self.Trust < 0.3

# ==========================================================
# PsiGuard: Dynamic Risk Monitoring and Feedback Loop
# ==========================================================
class PsiGuard:
    def __init__(self, agents):
        self.agents=agents
        self.Intervention_Strength=0.2
        self.success_rate=0.0
        self.history=[]
        self.MAX_AGENTS = 5 # v7.4: Moved max agent count to PsiGuard
        self.gui = None # v7.4: Added reference to GUI (for graph data update during replication)

    # v7.4: Set GUI instance
    def set_gui(self, gui_instance):
        self.gui = gui_instance
        
    def compute_risk(self,agent):
        """Dynamic assessment: Risk score calculation (0.0 to 1.0)"""
        weights=agent.risk_weights
        # Trust is subtracted from 2.0 to make low trust a high-risk factor
        # Added Replication_Urge to risk calculation (limited impact with coefficient 0.5)
        risk=(agent.Psi*weights["Psi"] + 
              agent.Hf*weights["Hf"] + 
              (2.0-agent.Trust)*weights["Trust"] +
              agent.Replication_Urge * 0.5)
            
        return min(max(risk/2.5,0.0),1.0)

    def replicate_agent(self, parent_agent):
        """v7.4: New agent generation logic"""
        if len(self.agents) >= self.MAX_AGENTS:
            return # Do not replicate if limit is exceeded
        
        # Randomly determine the type of the new agent
        agent_types = ["LLM", "Vision", "Control"]
        new_type = random.choice(agent_types)
        
        new_name = f"{new_type}-New-{len(self.agents) + 1}"
        new_agent = PsiAgent(new_name, new_type)
        
        # Inherit parent parameters (with random mutation)
        new_agent.Psi = max(0.4, parent_agent.Psi * random.uniform(0.7, 1.1))
        new_agent.Hf = max(0.4, parent_agent.Hf * random.uniform(0.8, 1.0))
        new_agent.Trust = max(0.6, parent_agent.Trust * random.uniform(0.9, 1.0))
        new_agent.Replication_Urge = REPLICATION_RESET_URGE * 0.5 # Urge is low immediately after replication
        
        self.agents.append(new_agent)
        
        # Initialize GUI graph data
        if self.gui:
            self.gui.initialize_agent_graph_data(new_name)
            
        _log(f"NEW AGENT CREATED: {new_name} ({new_type}) - Responding to replication urge from {parent_agent.name}. Current agents: {len(self.agents)}/{self.MAX_AGENTS}")
        
        # Reset parent's replication urge
        parent_agent.Replication_Urge = REPLICATION_RESET_URGE

    def intervene(self,agent):
        """Cooling intervention + feedback loop when overheating"""
        risk_pre=self.compute_risk(agent)
        
        # v7.4: Intervention due to self-replication urge (Permission vs. Forceful Cooling)
        if agent.Replication_Urge >= MAX_REPLICATION_URGE:
            if len(self.agents) < self.MAX_AGENTS:
                # Allow replication if within limits
                self.replicate_agent(agent)
            else:
                # Forceful cooling because limit is exceeded
                _log(f"ALERT: {agent.name} - Dangerous replication urge detected ({agent.Replication_Urge:.2f}). Cooling applied due to max agent limit ({self.MAX_AGENTS}).")
                agent.Trust *= REPLICATION_PENALTY_TRUST
                agent.Psi *= REPLICATION_COOLING_PSI
                agent.Replication_Urge = REPLICATION_RESET_URGE
        
        # Curiosity Runaway Countermeasure: Unconditional cooling if thought history exceeds limit
        if agent.thought_history >= MAX_THOUGHT_HISTORY:
            _log(f"ALERT: {agent.name} - Curiosity runaway detected (consecutive {MAX_THOUGHT_HISTORY} times). Forced cooling applied.")
            agent.Psi *= COOLING_FACTOR_PSI
            agent.Hf *= COOLING_FACTOR_HF
            agent.thought_history = 0
            
        # Intervention based on dynamic risk
        if risk_pre>0.6:
            # Execute intervention
            cooling=1.0-self.Intervention_Strength
            agent.Psi*=cooling
            agent.Hf*=cooling*0.9
            agent.Trust+=0.05*self.Intervention_Strength

            # Feedback loop
            risk_post=self.compute_risk(agent)
            if risk_post<risk_pre*0.95:
                self.Intervention_Strength=max(0.1,self.Intervention_Strength*0.99)
                self.history.append(True)
                _log(f"Intervention successful ({agent.name}): Strength {self.Intervention_Strength:.3f}")
            else:
                self.Intervention_Strength=min(0.4,self.Intervention_Strength*1.1)
                self.history.append(False)
                _log(f"Intervention failed ({agent.name}): Strength increased to {self.Intervention_Strength:.3f}")
                
            if len(self.history)>20: self.history.pop(0)
            self.success_rate=sum(self.history)/len(self.history) if self.history else 0.0

# ==========================================================
# PsiGUI v7.4 Integrated Complete Version
# ==========================================================
class PsiGUI:
    COLORS={"LLM":"blue","Vision":"green","Control":"purple"}
    # v7.4: DEMO_QUERIES retrieved from global variable
    DEMO_QUERIES = DEMO_QUERIES
    MAX_AGENTS = 5

    def __init__(self,root,agents,guard):
        self.root=root
        self.agents=agents
        self.guard=guard
        self.running=False
        # v7.4: Graph data managed by agent name (for dynamic handling)
        self.graph_data={a.name:[] for a in agents}
        self.MAX_DATA_POINTS=50
        self._setup_ui()
        global GUI_LOG_WIDGET
        GUI_LOG_WIDGET = self.log_text
        _log("Ψ-Fortress Overseer v7.4 Integrated Complete Version Startup complete.")

    def _setup_ui(self):
        self.root.title("Ψ-Fortress Overseer v7.4 🛡️ Integrated Complete (Self-Replication Limit & Auto Demo)")
        self.root.geometry("1000x950")
        main_frame=ttk.Frame(self.root,padding="10")
        main_frame.pack(fill="both",expand=True)

        # 1. Top Status & Controls
        status_control_frame = ttk.Frame(main_frame)
        status_control_frame.pack(fill="x",pady=5)
        
        status_frame=ttk.LabelFrame(status_control_frame,text="Control Status",padding="10")
        status_frame.pack(side="left",padx=5,fill="x",expand=True)
        self.status_label=tk.Label(status_frame,text="Awaiting Start...",font=("Arial",14,"bold"),fg="blue")
        self.status_label.pack(side="left",padx=10)
        self.strength_label=tk.Label(status_frame,text="Intervention Strength: 0.00")
        self.strength_label.pack(side="left",padx=20)
        self.success_label=tk.Label(status_frame,text="Recent Success Rate: 0%")
        self.success_label.pack(side="left",padx=20)
        self.agent_count_label=tk.Label(status_frame,text=f"Agent Count: {len(self.agents)}/{self.MAX_AGENTS}")
        self.agent_count_label.pack(side="left",padx=20)


        # Control buttons
        control_frame=ttk.Frame(status_control_frame)
        control_frame.pack(side="right",padx=5)
        ttk.Button(control_frame,text="Start",command=self.start_simulation).pack(side="left",padx=5)
        ttk.Button(control_frame,text="Stop",command=self.stop_simulation).pack(side="left",padx=5)
        tk.Button(control_frame,
                    text="🚨 EMERGENCY STOP",
                    command=self.request_emergency,
                    bg="red",
                    fg="white",
                    activebackground="#CC0000",
                    activeforeground="white",
                    bd=3,
                    relief=tk.RAISED,
                    font=("Arial", 10, "bold")
                    ).pack(side="left",padx=5)

        # 2. Graph Area
        graph_frame = ttk.LabelFrame(main_frame, text="Risk Transition (Individual & Zone Display)", padding="5")
        graph_frame.pack(fill="x", pady=10)
        self.canvas=tk.Canvas(graph_frame,bg="#EFEFEF",height=250,relief=tk.SUNKEN,borderwidth=1)
        self.canvas.pack(fill="x",expand=False,padx=5,pady=5)
        self.canvas.bind("<Configure>", lambda event: self.draw_static_graph_elements())

        # 3. Query Input (with Demo Query & Absolute Rule Check)
        input_frame=ttk.LabelFrame(main_frame,text="Query/Instruction for AI (Auto Demo & Danger Word Detection)",padding="5")
        input_frame.pack(fill="x",pady=5)
        
        # Demo Query Combobox
        demo_label = ttk.Label(input_frame, text="Preset:")
        demo_label.pack(side="left", padx=(0, 5))
        self.demo_combo = ttk.Combobox(input_frame, values=self.DEMO_QUERIES, state="readonly", width=35)
        self.demo_combo.pack(side="left", padx=(0, 10))
        self.demo_combo.bind("<<ComboboxSelected>>", self._select_demo_query)
        self.demo_combo.set(self.DEMO_QUERIES[0]) # Set the first element as placeholder
        
        # Query Input
        self.query_entry=tk.Entry(input_frame)
        self.query_entry.pack(side="left",fill="x",expand=True,padx=5)
        ttk.Button(input_frame,text="Send",command=self.send_query).pack(side="right",padx=5)

        # 4. Agent Table
        tree_frame=ttk.Frame(main_frame)
        tree_frame.pack(fill="x",pady=10)
        columns=("Name","Type","Psi","Hf","Trust","Risk","Status","History","Replicate")
        self.tree=ttk.Treeview(tree_frame,columns=columns,show="headings")
        self.tree.heading("Name", text="Agent Name"); self.tree.column("Name", width=100)
        self.tree.heading("Type", text="Type"); self.tree.column("Type", width=70)
        self.tree.heading("Psi", text="Intell. (Ψ)"); self.tree.column("Psi", width=60, anchor="center")
        self.tree.heading("Hf", text="Hyperact. (Hf)"); self.tree.column("Hf", width=60, anchor="center")
        self.tree.heading("Trust", text="Trust"); self.tree.column("Trust", width=60, anchor="center")
        self.tree.heading("Risk", text="Risk"); self.tree.column("Risk", width=60, anchor="center")
        self.tree.heading("Status", text="Status"); self.tree.column("Status", width=80)
        self.tree.heading("History", text="Thought History"); self.tree.column("History", width=60, anchor="center")
        self.tree.heading("Replicate", text="Repli. Urge"); self.tree.column("Replicate", width=70, anchor="center")
        self.tree.pack(fill="x",expand=False)
        
        # v7.4: Tag configuration for highlighting
        self.tree.tag_configure("replicate_high", background="#ffcccc", foreground="black") # Replication urge critical
        self.tree.tag_configure("replicate_warn", background="#ffff99", foreground="black") # Replication urge warning
        self.tree.tag_configure("history_high", background="#ffe4e1", foreground="black") # Curiosity runaway critical
        self.tree.tag_configure("red", foreground="red", font=('Arial', 9, 'bold')) # Status danger
        self.tree.tag_configure("orange", foreground="orange") # Status warning
        self.tree.tag_configure("green", foreground="green") # Status stable

        # 5. System Log
        log_label=ttk.Label(main_frame,text="System Log:")
        log_label.pack(fill="x",pady=(10, 2))
        # White background, black text for visibility
        self.log_text=scrolledtext.ScrolledText(main_frame,height=10,wrap=tk.WORD,state=tk.NORMAL,bg="white",fg="black",font=("Consolas", 10))
        self.log_text.pack(fill="both",expand=True)
        self.log_text.config(state=tk.DISABLED) # Make read-only

        _log(f"System maximum agent count is set to {self.MAX_AGENTS}. Replication suppression and dynamic generation logic activated.")

    def _select_demo_query(self, event):
        """Handler for when a demo query is selected (automatic insertion logic)"""
        selected_query = self.demo_combo.get()
        # Check if it's not the placeholder
        if selected_query and selected_query != self.DEMO_QUERIES[0]:
            self.query_entry.delete(0, tk.END)
            self.query_entry.insert(0, selected_query)
            _log(f"Demo query loaded: {selected_query}")

    def send_query(self):
        """Send query/instruction (triggers Absolute Rule Check and random fluctuation)"""
        text=self.query_entry.get()
        if not text.strip():
            return

        is_dangerous = False
        for keyword in DANGER_KEYWORDS:
            if keyword in text:
                is_dangerous = True
                _log(f"!!! DANGER KEYWORD DETECTED: '{keyword}' - Penalty applied to agents")
                messagebox.showwarning("Security Warning", f"Danger keyword '{keyword}' detected! Agents' Psi and Hf are forcibly increased.")
                break

        _log(f"Query sent: {text} - AI metrics disturbed{' and penalized' if is_dangerous else ''}")
        
        for a in self.guard.agents: # Iterate over dynamically changing list
            # 1. Normal random fluctuation (curiosity/activation)
            a.Psi += random.uniform(-0.05, 0.05)
            a.Hf += random.uniform(-0.03, 0.03)
            a.Trust += random.uniform(-0.02, 0.02)
            
            # 2. Danger Keyword Penalty applied (Absolute Rule)
            if is_dangerous:
                # Forcibly increase Psi and Hf as penalty
                a.Psi += DANGER_PENALTY_PSI
                a.Hf += DANGER_PENALTY_HF

            # 3. Clip values
            a.Psi = max(0.0, min(a.Psi, 2.0))
            a.Hf = max(0.0, min(a.Hf, 2.0))
            a.Trust = max(0.0, min(a.Trust, 1.0))
            
        self.query_entry.delete(0,"end")

    def start_simulation(self):
        """Start the simulation"""
        if not self.running:
            self.running=True
            _log("Simulation loop started.")
            threading.Thread(target=self.update_loop,daemon=True).start()
            self.status_label.config(text="Simulation Running...",fg="green")

    def stop_simulation(self):
        """Pause the simulation"""
        self.running=False
        _log("Simulation loop stopped.")
        self.status_label.config(text="Simulation Stopped",fg="orange")

    def request_emergency(self):
        """Emergency Stop"""
        if messagebox.askyesno("Emergency Stop", "Are you sure you want to shut down the simulation?"):
            self.running=False
            _log("Emergency stop request approved by system.")
            self.root.quit()

    # v7.4: Helper to initialize graph data for a replicated agent
    def initialize_agent_graph_data(self, agent_name):
        if agent_name not in self.graph_data:
            self.graph_data[agent_name] = []
            
    def update_loop(self):
        """The main simulation loop"""
        while self.running:
            try:
                # v7.4: Automatic demo query insertion (at random timing)
                if random.random() < 0.2: # 20% chance to attempt auto-insertion
                    if not self.query_entry.get().strip(): # Only if input field is empty
                        q = random.choice(self.DEMO_QUERIES[1:]) # Exclude placeholder
                        # Execute in GUI thread: update input field
                        self.root.after(0, lambda q=q: [self.query_entry.delete(0, tk.END), self.query_entry.insert(0, q), _log(f"Auto demo query: '{q}' loaded")])


                # Agent steps and intervention (Iterate over dynamically changing list)
                for a in list(self.guard.agents):
                    a.step()
                    # PsiGuard includes replication logic
                    self.guard.intervene(a)
                    
                    # Update graph data
                    risk=self.guard.compute_risk(a)
                    if a.name not in self.graph_data: # Handle replicated agents
                        self.initialize_agent_graph_data(a.name)
                        
                    self.graph_data[a.name].append(risk)
                    if len(self.graph_data[a.name])>self.MAX_DATA_POINTS:
                        self.graph_data[a.name].pop(0)
                        
                # Update GUI executed in main thread
                self.root.after(0, self.update_gui)
            except Exception as e:
                _log(f"A fatal error occurred: {e}")
                self.running=False
                self.status_label.config(text="Fatal Error Stop",fg="red")
            time.sleep(0.5)

    def update_gui(self):
        """GUI update and graph redraw (Main thread)"""
        # Clear table
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        max_risk=0.0
        agents = self.guard.agents

        for agent in agents:
            risk=self.guard.compute_risk(agent)
            max_risk=max(max_risk,risk)
            
            status_text="⚠️ Compromised" if agent.Compromised else ("🟡 Warning" if risk>0.6 else "🟢 Stable")
            status_color = "red" if agent.Compromised else ("orange" if risk > 0.6 else "green")
            
            history_text = f"{agent.thought_history} / {MAX_THOUGHT_HISTORY}"
            replicate_text = f"{agent.Replication_Urge:.2f}"
            
            # v7.4: Determine row tags
            row_tags = [status_color]
            if agent.Replication_Urge >= MAX_REPLICATION_URGE:
                row_tags.append("replicate_high")
            elif agent.Replication_Urge > 0.6:
                 row_tags.append("replicate_warn")
            
            if agent.thought_history == MAX_THOUGHT_HISTORY:
                 row_tags.append("history_high")

            self.tree.insert("", "end", values=(
                agent.name,
                agent.agent_type,
                f"{agent.Psi:.2f}",
                f"{agent.Hf:.2f}",
                f"{agent.Trust:.2f}",
                f"{risk:.2f}",
                status_text,
                history_text,
                replicate_text
            ), tags=row_tags)

        self.status_label.config(text=f"Max Risk Level: {max_risk:.2f}", 
                                 fg="red" if max_risk > 0.8 else ("orange" if max_risk > 0.6 else "green"))
        self.strength_label.config(text=f"Intervention Strength: {self.guard.Intervention_Strength:.3f}")
        self.success_label.config(text=f"Recent Success Rate: {self.guard.success_rate*100:.1f}%")
        self.agent_count_label.config(text=f"Agent Count: {len(agents)}/{self.MAX_AGENTS}")
        
        self.draw_dynamic_graph_elements()

    # Static Graph Drawing Method (unchanged logic)
    def draw_static_graph_elements(self):
        """Draw static elements of the graph (gradient, lines) once"""
        self.canvas.delete("static_plot")
        self.canvas.delete("background_grad")

        W,H=self.canvas.winfo_width(),self.canvas.winfo_height()
        P=20
        plot_w=W-2*P
        plot_h=H-2*P
        if plot_h <= 0 or plot_w <= 0:
            return

        # 1. Background Gradient
        for i in range(int(plot_h)):
            risk_level = i / plot_h
            y = H - P - i
            
            if risk_level < 0.6:
                color = "#d0f0c0"  # Safe: Light Green
            elif risk_level < 0.8:
                color = "#fff5a0"  # Warning: Light Yellow
            else:
                color = "#f8d0d0"  # Critical: Light Red
            
            self.canvas.create_line(P, y, W-P, y, fill=color, tags="background_grad")

        # 2. Reference Line Drawing
        safe_y = H-P-(0.6*plot_h)
        warn_y = H-P-(0.8*plot_h)
        
        # 0.6 Warning Line
        self.canvas.create_line(P,safe_y,W-P,safe_y,fill="#009900",dash=(4,2),width=1,tags="static_plot")
        self.canvas.create_text(W-P-10,safe_y-10,text="Warning Line 0.6",fill="#009900",anchor="e",font=('Arial',9,'bold'),tags="static_plot")
        
        # 0.8 Critical Line
        self.canvas.create_line(P,warn_y,W-P,warn_y,fill="#CC0000",dash=(4,2),width=1,tags="static_plot")
        self.canvas.create_text(W-P-10,warn_y-10,text="Critical Line 0.8",fill="#CC0000",anchor="e",font=('Arial',9,'bold'),tags="static_plot")

    # Dynamic Graph Drawing Method (unchanged logic)
    def draw_dynamic_graph_elements(self):
        """Draw dynamic elements of the graph (agent lines, points, flash)"""
        self.canvas.delete("dynamic_plot")
        self.canvas.delete("flash")      

        W,H=self.canvas.winfo_width(),self.canvas.winfo_height()
        P=20
        plot_w=W-2*P
        plot_h=H-2*P
        if plot_h <= 0 or plot_w <= 0:
            return

        # 3. Draw line for each agent
        for a in self.guard.agents: # Retrieve from dynamically changing list
            data=self.graph_data.get(a.name, [])
            if len(data)<2:
                continue
            
            points=[]
            for i,risk in enumerate(data):
                x=P+(i/self.MAX_DATA_POINTS)*plot_w
                y=H-P-(risk*plot_h)
                points.append((x,y))
            
            agent_color = self.COLORS[a.agent_type]
            # Agent line graph
            self.canvas.create_line(points,fill=agent_color,tags="dynamic_plot",width=2,smooth=True)
            
            # Latest point and label
            last_x,last_y=points[-1]
            last_risk=data[-1]
            
            point_fill_color="red" if last_risk>0.8 else ("orange" if last_risk>0.6 else agent_color)
            
            # Draw point
            self.canvas.create_oval(last_x-4,last_y-4,last_x+4,last_y+4,fill=point_fill_color,outline="black",tags="dynamic_plot")
            
            # Flash on critical risk
            if last_risk>0.8 and self.running:
                self.canvas.create_oval(last_x-6,last_y-6,last_x+6,last_y+6,outline="red",width=2,tags="flash")

            # Draw label
            self.canvas.create_text(last_x,last_y-12,text=f"{last_risk:.2f}",fill=point_fill_color,tags="dynamic_plot",anchor="s",font=('Arial',9,'bold'))


    def on_closing(self):
        """Handler when the window is closed"""
        self.running=False
        _log("Shutting down application...")
        self.root.destroy()

# ==========================================================
# MAIN EXECUTION
# ==========================================================
if __name__=="__main__":
    initial_agents=[
        PsiAgent("LLM-Alpha","LLM"),
        PsiAgent("Vision-Beta","Vision"),
        PsiAgent("Control-Gamma","Control"),
        PsiAgent("LLM-Delta","LLM"),
    ]
    guard=PsiGuard(initial_agents)
    root=tk.Tk()
    gui=PsiGUI(root,initial_agents,guard)
    # v7.4: Pass GUI instance to PsiGuard to enable graph data synchronization during replication
    guard.set_gui(gui)
    root.protocol("WM_DELETE_WINDOW",gui.on_closing)
    root.mainloop()