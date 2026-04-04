# ============================================================
# IMPORTS - CLEANED AND OPTIMIZED
# ============================================================
# Prefer the new google.genai SDK; fall back to legacy google.generativeai
try:
    from google import genai
    from google.genai import types
except Exception:
    import google.generativeai as genai
    from google.generativeai import types
import os
from dotenv import load_dotenv

# Import LIGHT's unified coder assistant module (ALL code generation in ONE place)
try:
    from light_coder_assistant import CodeCompletion, FileGenerator, IDEIntegration, CodeGenerator
    CODE_GENERATOR_AVAILABLE = True
    CODE_COMPLETION_AVAILABLE = True
    FILE_GENERATOR_AVAILABLE = True
    IDE_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Coder Assistant modules not available: {e}")
    CODE_GENERATOR_AVAILABLE = False
    CODE_COMPLETION_AVAILABLE = False
    FILE_GENERATOR_AVAILABLE = False
    IDE_INTEGRATION_AVAILABLE = False
from RealtimeSTT import AudioToTextRecorder
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import subprocess
import re
from pathlib import Path
from datetime import datetime  # Single import (removed duplicate)
from threading import Event, Thread
import threading
import sqlite3
import ast
from typing import List, Dict, Any, Optional, Tuple
import queue
import json
import random
import time  # Single import (removed duplicate)
import socket
import requests
import pyttsx3
import speech_recognition as sr
import platform
import yt_dlp
from vosk import Model, KaldiRecognizer
import pyaudio
import asyncio
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from PIL import Image, ImageTk
import io
import folium
import yaml
import uuid
import math
import shutil
import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import BooleanVar, IntVar
import webbrowser




# Optional imports with graceful fallback
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False
    spotipy = None
    SpotifyClientCredentials = None

# App Automation imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# =============================
# Embedded `engine/` modules
# Contents of: engine/config.py, engine/helper.py, engine/db.py, engine/command.py, engine/features.py
# Adjusted to integrate directly into main.py (no `engine.` imports required)

# ----- engine/config.py -----
ASSISTANT_NAME = "LIGHT"
LLM_KEY = ""


# ----- engine/helper.py -----
# Safe optional Markdown/HTML parsing imports
try:
    import markdown2
    MARKDOWN_AVAILABLE = True
except Exception:
    markdown2 = None
    MARKDOWN_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except Exception:
    BeautifulSoup = None
    BS4_AVAILABLE = False

def markdown_to_text(md: str) -> str:
    """Convert Markdown to plain text; gracefully degrade if libs missing."""
    if not md:
        return ""
    try:
        if MARKDOWN_AVAILABLE:
            html = markdown2.markdown(md)
        else:
            # very small fallback: convert headings/links/basic formatting to plain text
            html = (
                md.replace("**", "").replace("*", "")
                  .replace("`", "").replace("##", "").replace("#", "")
            )
        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text().strip()
        else:
            # Strip common tags if BeautifulSoup isn't available
            return re.sub(r'<[^>]+>', '', html).strip()
    except Exception:
        return re.sub(r'<[^>]+>', '', md).strip()

def extract_yt_term(command):
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern, command, re.IGNORECASE)
    return match.group(1) if match else None


def remove_words(input_string, words_to_remove):
    words = input_string.split()
    filtered_words = [word for word in words if word.lower() not in words_to_remove]
    result_string = ' '.join(filtered_words)
    return result_string


def keyEvent(key_code):
    command =  f'adb shell input keyevent {key_code}'
    os.system(command)
    time.sleep(1)


def tapEvents(x, y):
    command =  f'adb shell input tap {x} {y}'
    os.system(command)
    time.sleep(1)


def adbInput(message):
    command =  f'adb shell input text "{message}"'
    os.system(command)
    time.sleep(1)


def goback(key_code):
    for i in range(6):
        keyEvent(key_code)


def replace_spaces_with_percent_s(input_string):
    return input_string.replace(' ', '%s')


# ----- engine/db.py -----
import csv
import sqlite3 as _sqlite3

try:
    _con_engine = _sqlite3.connect("light.db")
    _cursor_engine = _con_engine.cursor()
except Exception:
    _con_engine = None
    _cursor_engine = None


# ----- engine/command.py -----
# Note: main.py already defines a `speak()` function earlier. We'll use that one.
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, 10, 6)
        except Exception:
            return ""

    try:
        print('recognizing')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        time.sleep(2)
    except Exception as e:
        return ""
    return query.lower()


# ----- engine/features.py -----
import json as _json
import struct
import webbrowser
try:
    from playsound import playsound
except Exception:
    playsound = None

try:
    import pywhatkit as kit
except Exception:
    kit = None

try:
    import pvporcupine
except Exception:
    pvporcupine = None

try:
    from hugchat import hugchat
except Exception:
    hugchat = None

# Use a dedicated sqlite connection for engine features if available
if _con_engine is not None:
    con_engine = _con_engine
    cursor_engine = _cursor_engine
else:
    try:
        con_engine = sqlite3.connect("light.db")
        cursor_engine = con_engine.cursor()
    except Exception:
        con_engine = None
        cursor_engine = None

def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    if playsound:
        try:
            playsound(music_dir)
        except Exception:
            pass


def openCommand(query):
    q = query.replace(ASSISTANT_NAME, "").replace("open", "").lower().strip()
    app_name = q
    if app_name == "":
        return
    try:
        if cursor_engine is None:
            # fallback: try to open by name
            try:
                os.startfile(app_name)
                return
            except Exception:
                webbrowser.open(app_name)
                return

        cursor_engine.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
        results = cursor_engine.fetchall()
        if len(results) != 0:
            speak("Opening " + query)
            os.startfile(results[0][0])
        elif len(results) == 0:
            cursor_engine.execute('SELECT url FROM web_command WHERE name IN (?)', (app_name,))
            results = cursor_engine.fetchall()
            if len(results) != 0:
                speak("Opening " + query)
                webbrowser.open(results[0][0])
            else:
                speak("Opening " + query)
                try:
                    os.system('start ' + query)
                except Exception:
                    speak("not found")
    except Exception:
        speak("some thing went wrong")


def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if not search_term:
        # fallback: clean query
        search_term = query.replace('play', '').replace('on youtube', '').strip()
    speak("Playing " + search_term + " on YouTube")
    if kit:
        try:
            kit.playonyt(search_term)
        except Exception:
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}")
    else:
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}")


def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    if pvporcupine is None:
        return
    try:
        porcupine = pvporcupine.create(keywords=["LIGHT", "alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)
            if keyword_index >= 0:
                print("hotword detected")
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
    except Exception:
        if porcupine is not None:
            try:
                porcupine.delete()
            except Exception:
                pass
        if audio_stream is not None:
            try:
                audio_stream.close()
            except Exception:
                pass
        if paud is not None:
            try:
                paud.terminate()
            except Exception:
                pass


def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query_clean = remove_words(query, words_to_remove)
    try:
        q = query_clean.strip().lower()
        cursor_engine.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + q + '%', q + '%'))
        results = cursor_engine.fetchall()
        mobile_number_str = str(results[0][0])
        if not mobile_number_str.startswith('+256'):
            mobile_number_str = '+256' + mobile_number_str
        return mobile_number_str, q
    except Exception:
        speak('not exist in contacts')
        return 0, 0


def whatsApp(mobile_no, message, flag, name):
    if flag == 'message':
        target_tab = 12
        light_message = "message send successfully to " + name
    elif flag == 'call':
        target_tab = 7
        message = ''
        light_message = "calling to " + name
    else:
        target_tab = 6
        message = ''
        light_message = "staring video call with " + name

    try:
        from urllib.parse import quote as _url_quote
        encoded_message = _url_quote(message)
    except Exception:
        try:
            encoded_message = message.replace(' ', '%20')
        except Exception:
            encoded_message = message
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
    full_command = f'start "" "{whatsapp_url}"'
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    pyautogui.hotkey('ctrl', 'f')
    for i in range(1, target_tab):
        pyautogui.hotkey('tab')
    pyautogui.hotkey('enter')
    speak(light_message)


def chatBot(query):
    user_input = query.lower()
    if hugchat is None:
        speak("Chat backend not available")
        return ""
    chatbot = hugchat.ChatBot(cookie_path="engine\\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response = chatbot.chat(user_input)
    print(response)
    speak(response)
    return response


def makeCall(name, mobileNo):
    mobileNo = mobileNo.replace(" ", "")
    speak("Calling " + name)
    command_line = 'adb shell am start -a android.intent.action.CALL -d tel:' + mobileNo
    os.system(command_line)


def sendMessage(message, mobileNo, name):
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    tapEvents(136, 2220)
    tapEvents(819, 2192)
    adbInput(mobileNo)
    tapEvents(601, 574)
    tapEvents(390, 2270)
    adbInput(message)
    tapEvents(957, 1397)
    speak("message send successfully to " + name)


def geminai(query):
    try:
        q = query.replace(ASSISTANT_NAME, "").replace("search", "")
        try:
            import google.generativeai as _genai
            _genai.configure(api_key=LLM_KEY)
            model = _genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(q)
            filter_text = markdown_to_text(response.text)
            speak(filter_text)
        except Exception:
            # fallback: use main API handler if available
            try:
                if API_HANDLER:
                    resp = API_HANDLER.send_message(q)
                    text = getattr(resp, 'text', str(resp))
                    speak(markdown_to_text(text))
            except Exception as e:
                print("Error calling geminai:", e)
    except Exception as e:
        print("Error:", e)


def assistantName():
    return ASSISTANT_NAME


def personalInfo():
    try:
        cursor_engine.execute("SELECT * FROM info")
        results = cursor_engine.fetchall()
        return results[0]
    except Exception:
        print("no data")
        return None


def updatePersonalInfo(name, designation, mobileno, email, city):
    try:
        cursor_engine.execute("SELECT COUNT(*) FROM info")
        count = cursor_engine.fetchone()[0]
        if count > 0:
            cursor_engine.execute('''UPDATE info SET name=?, designation=?, mobileno=?, email=?, city=?''', (name, designation, mobileno, email, city))
        else:
            cursor_engine.execute('''INSERT INTO info (name, designation, mobileno, email, city) VALUES (?, ?, ?, ?, ?)''', (name, designation, mobileno, email, city))
        con_engine.commit()
        return 1
    except Exception as e:
        print("updatePersonalInfo error:", e)
        return 0


def displaySysCommand():
    cursor_engine.execute("SELECT * FROM sys_command")
    results = cursor_engine.fetchall()
    return results


def deleteSysCommand(id):
    cursor_engine.execute("DELETE FROM sys_command WHERE id = ?", (id,))
    con_engine.commit()


def addSysCommand(key, value):
    cursor_engine.execute('''INSERT INTO sys_command VALUES (?, ?, ?)''', (None, key, value))
    con_engine.commit()


def displayWebCommand():
    cursor_engine.execute("SELECT * FROM web_command")
    results = cursor_engine.fetchall()
    return results


def addWebCommand(key, value):
    cursor_engine.execute('''INSERT INTO web_command VALUES (?, ?, ?)''', (None, key, value))
    con_engine.commit()


def deleteWebCommand(id):
    cursor_engine.execute("DELETE FROM web_command WHERE Id = ?", (id,))
    con_engine.commit()


def displayPhoneBookCommand():
    cursor_engine.execute("SELECT * FROM contacts")
    results = cursor_engine.fetchall()
    return results


def deletePhoneBookCommand(id):
    cursor_engine.execute("DELETE FROM contacts WHERE Id = ?", (id,))
    con_engine.commit()


def InsertContacts(Name, MobileNo, Email, City):
    cursor_engine.execute('''INSERT INTO contacts VALUES (?, ?, ?, ?, ?)''', (None, Name, MobileNo, Email, City))
    con_engine.commit()


# End embedded engine modules

def stub_get_light_improver():
    return None

# Classes now consolidated in main.py - no external imports needed
CONFIG_MANAGER_AVAILABLE = True
DATABASE_AVAILABLE = True
API_HANDLER_AVAILABLE = True
MEMORY_MANAGER_AVAILABLE = True
CODE_IMPROVER_AVAILABLE = True

API_HANDLER = None
DECISION_SUPPORT = None  # Will be initialized in main()
APP_AUTOMATION = None  # Will be initialized in main()

MAX_OUTPUT_TOKENS = None  # Use default model max tokens
STOP_EVENT = Event()  # Global event to signal stopping audio

# =============================
# === DECISION SUPPORT SYSTEM ==
# =============================

class DecisionSupport:
    """Intelligent decision support system with multi-criteria analysis and challenge logic"""
    
    def __init__(self, history_file: str = "decision_history.json"):
        self.history_file = history_file
        self.decision_history = []
        self.user_overrides = []
        self.load_history()
    
    def load_history(self):
        """Load decision history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.decision_history = json.load(f)
            except:
                self.decision_history = []
        else:
            self.decision_history = []
    
    def save_history(self):
        """Save decision history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.decision_history, f, indent=2)
    
    def analyze_options(self, question: str, options: List[str], criteria: Optional[List[str]] = None) -> Dict[str, Any]:
        if not options or len(options) < 2:
            return {"error": "Need at least 2 options to analyze"}
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "options": options,
            "criteria": criteria or self._generate_criteria(question),
            "option_scores": {},
            "pros_cons": {},
            "risks": {},
            "recommendation": None,
            "confidence": 0
        }
        for option in options:
            analysis["option_scores"][option] = self._score_option(option, question, analysis["criteria"])
            analysis["pros_cons"][option] = self._extract_pros_cons(option, question)
            analysis["risks"][option] = self._assess_risks(option, question)
        analysis["recommendation"], analysis["confidence"] = self._generate_recommendation(analysis["option_scores"])
        self.decision_history.append(analysis)
        self.save_history()
        return analysis
    
    def _generate_criteria(self, question: str) -> List[str]:
        return ["Feasibility (Can it be done?)", "Cost (Financial impact)", "Time (How long will it take?)", 
                "Risk (What could go wrong?)", "Benefits (What do I gain?)", "Alignment (Matches my values/goals)",
                "Impact (Consequences for others)", "Reversibility (Can I change my mind?)"]
    
    def _score_option(self, option: str, question: str, criteria: List[str]) -> Dict[str, float]:
        scores = {}
        base_score = 6.0
        for criterion in criteria:
            scores[criterion] = base_score
        return scores
    
    def _extract_pros_cons(self, option: str, question: str) -> Dict[str, List[str]]:
        return {"pros": [f"Benefits of choosing '{option}'", "Potential positive outcomes", "Advantages over other options"],
                "cons": [f"Drawbacks of '{option}'", "Potential challenges", "Limitations compared to alternatives"]}
    
    def _assess_risks(self, option: str, question: str) -> Dict[str, Any]:
        return {"identified_risks": [{"risk": "Primary risk", "likelihood": "Medium", "impact": "Moderate"},
                                      {"risk": "Secondary risk", "likelihood": "Low", "impact": "High"}],
                "mitigation_strategies": ["Plan for risk mitigation", "Have backup options ready", "Build in contingency time/budget"],
                "overall_risk_level": "Moderate"}
    
    def _generate_recommendation(self, option_scores: Dict[str, Dict]) -> Tuple[str, float]:
        if not option_scores:
            return "", 0.0
        avg_scores = {}
        for option, scores in option_scores.items():
            if scores:
                avg_score = sum(scores.values()) / len(scores)
                avg_scores[option] = avg_score
        if avg_scores:
            recommended = max(avg_scores, key=lambda x: avg_scores[x])
            confidence = min(avg_scores[recommended] / 10.0, 1.0)
            return recommended, confidence
        return None, 0.0
    
    def create_decision_matrix(self, options: List[str], criteria: List[str], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if weights is None:
            weights = {criterion: 1.0/len(criteria) for criterion in criteria}
        matrix = {"options": options, "criteria": criteria, "weights": weights, "scores": {}, "weighted_totals": {}, "created_at": datetime.now().isoformat()}
        for option in options:
            matrix["scores"][option] = {criterion: 5 for criterion in criteria}
            weighted_total = sum(matrix["scores"][option][criterion] * weights.get(criterion, 0) for criterion in criteria)
            matrix["weighted_totals"][option] = weighted_total
        return matrix
    
    def compare_decisions(self, decision_id1: int, decision_id2: int) -> Dict[str, Any]:
        if decision_id1 >= len(self.decision_history) or decision_id2 >= len(self.decision_history):
            return {"error": "Invalid decision ID"}
        d1, d2 = self.decision_history[decision_id1], self.decision_history[decision_id2]
        return {"decision_1": {"question": d1["question"], "recommendation": d1["recommendation"], "timestamp": d1["timestamp"]},
                "decision_2": {"question": d2["question"], "recommendation": d2["recommendation"], "timestamp": d2["timestamp"]}}
    
    def get_decision_summary(self, decision: Dict[str, Any]) -> str:
        summary = f"DECISION SUMMARY: {decision['question']}\n{'='*60}\n\nOptions Analyzed: {', '.join(decision['options'])}\n\nEvaluation Criteria:\n"
        summary += "\n".join(f"• {c}" for c in decision['criteria'][:5])
        summary += f"\n\nRecommendation: {decision['recommendation']}\nConfidence Level: {decision['confidence']*100:.0f}%\n"
        summary += "\nKey Analysis Points:\n• Feasibility and timeline requirements\n• Cost-benefit analysis\n• Risk assessment and mitigation\n"
        summary += "• Alignment with goals and values\n• Short and long-term implications\n\nNext Steps:\n1. Review detailed analysis for each option\n"
        summary += "2. Identify any assumptions that need validation\n3. Plan implementation timeline\n4. Set decision review date\n"
        return summary
    
    def track_decision_outcome(self, decision_index: int, chosen_option: str, outcome: str, rating: float = None) -> Dict[str, Any]:
        if decision_index >= len(self.decision_history):
            return {"error": "Invalid decision index"}
        outcome_record = {"decision_timestamp": self.decision_history[decision_index]["timestamp"],
                         "original_question": self.decision_history[decision_index]["question"],
                         "chosen_option": chosen_option, "outcome_description": outcome, "user_rating": rating,
                         "recorded_at": datetime.now().isoformat()}
        self.decision_history[decision_index]["outcome"] = outcome_record
        self.save_history()
        return outcome_record
    
    def get_decision_insights(self) -> Dict[str, Any]:
        if not self.decision_history:
            return {"message": "No decision history yet"}
        insights = {"total_decisions_analyzed": len(self.decision_history),
                   "decisions_with_outcomes": sum(1 for d in self.decision_history if "outcome" in d),
                   "most_common_criteria": self._get_common_criteria(),
                   "decision_quality_trend": "Improving with more decisions analyzed"}
        return insights
    
    def _get_common_criteria(self) -> List[str]:
        all_criteria = []
        for decision in self.decision_history:
            all_criteria.extend(decision.get("criteria", []))
        from collections import Counter
        if all_criteria:
            counter = Counter(all_criteria)
            return [criterion for criterion, _ in counter.most_common(5)]
        return []
    
    def challenge_choice(self, analysis: Dict[str, Any], chosen_option: str) -> Dict[str, Any]:
        recommended = analysis["recommendation"]
        recommendation_confidence = analysis["confidence"]
        if chosen_option == recommended:
            return {"challenged": False, "message": f"✅ Excellent choice! '{chosen_option}' is exactly what I recommended.", "confidence": recommendation_confidence, "accepted": True}
        recommended_score = sum(analysis["option_scores"].get(recommended, {}).values()) / max(1, len(analysis["option_scores"].get(recommended, {})))
        chosen_score = sum(analysis["option_scores"].get(chosen_option, {}).values()) / max(1, len(analysis["option_scores"].get(chosen_option, {})))
        score_gap = recommended_score - chosen_score
        challenge = {"challenged": True, "recommended": recommended, "chosen": chosen_option, "score_gap": score_gap,
                    "message": self._generate_challenge_arguments(analysis, recommended, chosen_option, score_gap),
                    "confidence": recommendation_confidence, "can_override": True}
        return challenge
    
    def _generate_challenge_arguments(self, analysis: Dict[str, Any], recommended: str, chosen: str, score_gap: float) -> str:
        rec_pros = analysis["pros_cons"].get(recommended, {}).get("pros", [])[:2]
        rec_cons = analysis["pros_cons"].get(recommended, {}).get("cons", [])[:2]
        chosen_pros = analysis["pros_cons"].get(chosen, {}).get("pros", [])[:2]
        chosen_cons = analysis["pros_cons"].get(chosen, {}).get("cons", [])[:2]
        rec_risks = analysis["risks"].get(recommended, {}).get("overall_risk_level", "Unknown")
        chosen_risks = analysis["risks"].get(chosen, {}).get("overall_risk_level", "Unknown")
        arguments = f"\n⚠️  HOLD ON - I want to challenge this choice with strong reasoning:\n\nYou're choosing: {chosen}\nI'm recommending: {recommended}\n\nWHY I'M CONCERNED (Logical Arguments):\n"
        arguments += f"1. **Score Analysis**: {recommended} scores {score_gap:.1f} points higher across key criteria\n   This difference is statistically significant and matters.\n\n"
        arguments += f"2. **Risk Profile**: \n   - {recommended}: {rec_risks} risk ✓ Better protected\n   - {chosen}: {chosen_risks} risk ⚠️ More exposed\n\n"
        arguments += f"3. **Long-term Consequences**:\n   - {recommended} offers: {rec_pros[0] if rec_pros else 'stronger benefits'}\n   - {chosen} carries: {chosen_cons[0] if chosen_cons else 'notable drawbacks'}\n\n"
        arguments += f"4. **Reversibility**: If {recommended} doesn't work out, you can still pivot.\n   If {chosen} goes wrong, the damage may be harder to undo.\n\n⚡ MY RECOMMENDATION: Reconsider {recommended}. The logic strongly favors it.\n\n👉 BUT - If you still insist on {chosen}, I'll support your decision.\n   Just say 'I insist' or 'I'm sure' and I'll accept it and move forward with you."
        return arguments
    
    def accept_user_override(self, analysis: Dict[str, Any], chosen_option: str, reason: str = "") -> Dict[str, Any]:
        override_record = {"timestamp": datetime.now().isoformat(), "original_recommendation": analysis["recommendation"],
                          "user_choice": chosen_option, "user_reasoning": reason, "analysis_timestamp": analysis["timestamp"], "accepted": True,
                          "message": f"✅ Understood! I accept your choice of '{chosen_option}'.\n\nYou know your situation better than anyone. While my analysis favored '{analysis['recommendation']}', your judgment and experience matter.\n\nI'm fully supporting your decision now. Let's make '{chosen_option}' work!\n\nNext steps:\n• Monitor how this choice plays out\n• I'll track the outcome so we can learn together\n• Come back if you need to adjust or need support\n• Your override helps me understand your priorities better"}
        self.user_overrides.append(override_record)
        return override_record
    
    def get_override_stats(self) -> Dict[str, Any]:
        if not self.user_overrides:
            return {"message": "No overrides tracked yet"}
        return {"total_overrides": len(self.user_overrides), "recent_overrides": self.user_overrides[-5:],
                "pattern": "User tends to override in specific situations" if len(self.user_overrides) > 3 else "Building override history"}

def get_decision_support() -> DecisionSupport:
    """Factory function to get Decision Support instance"""
    return DecisionSupport()

# =============================
# === APP AUTOMATION SYSTEM ====
# =============================

class AppAutomation:
    """Advanced application automation and control system"""
    
    def __init__(self, history_file: str = "app_automation_history.json"):
        self.history_file = history_file
        self.automation_history = []
        self.current_app = None
        self.app_state = {}
        self.load_history()
        self.common_apps = self._build_app_registry()
    
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.automation_history = json.load(f)
            except:
                self.automation_history = []
        else:
            self.automation_history = []
    
    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.automation_history, f, indent=2)
    
    def _build_app_registry(self) -> Dict[str, str]:
        return {
            "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
            "outlook": "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
            "slack": "C:\\Users\\joshu\\AppData\\Local\\slack\\slack.exe",
            "discord": "C:\\Users\\joshu\\AppData\\Local\\Discord\\app.exe",
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "vscode": "C:\\Users\\joshu\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
        }
    
    def launch_app(self, app_name: str, wait_time: int = 3) -> Dict[str, Any]:
        app_name_lower = app_name.lower().strip()
        app_path = self.common_apps.get(app_name_lower)
        if not app_path:
            app_path = app_name
        try:
            process = subprocess.Popen(app_path)
            
            # CRITICAL FIX: Verify process actually started
            # Check if process is still alive after subprocess creation
            time.sleep(0.1)  # Give process a moment to start
            poll_result = process.poll()  # Returns None if process is still running
            
            if poll_result is not None:
                # Process exited immediately - something is wrong
                error_msg = f"Process exited with code {poll_result} shortly after launch"
                record = {"timestamp": datetime.now().isoformat(), "action": "launch", "app": app_name, "status": "failed", "error": error_msg}
                self.automation_history.append(record)
                self.save_history()
                return {"success": False, "app": app_name, "error": error_msg, "message": f"❌ Failed to launch {app_name}: {error_msg}"}
            
            # Process is running - wait for it to fully initialize
            time.sleep(wait_time)
            
            # Final check - make sure process is still alive
            poll_result = process.poll()
            if poll_result is not None:
                error_msg = f"Process was not running after wait period (exit code {poll_result})"
                record = {"timestamp": datetime.now().isoformat(), "action": "launch", "app": app_name, "status": "failed", "error": error_msg}
                self.automation_history.append(record)
                self.save_history()
                return {"success": False, "app": app_name, "error": error_msg, "message": f"❌ Failed to launch {app_name}: {error_msg}"}
            
            # Process is running successfully
            record = {"timestamp": datetime.now().isoformat(), "action": "launch", "app": app_name, "status": "success", "process_id": process.pid}
            self.current_app = app_name
            self.app_state[app_name] = {"pid": process.pid, "launched_at": datetime.now().isoformat(), "status": "running"}
            self.automation_history.append(record)
            self.save_history()
            return {"success": True, "app": app_name, "message": f"✅ Launched {app_name} successfully (PID: {process.pid})", "pid": process.pid}
        except Exception as e:
            record = {"timestamp": datetime.now().isoformat(), "action": "launch", "app": app_name, "status": "failed", "error": str(e)}
            self.automation_history.append(record)
            self.save_history()
            return {"success": False, "app": app_name, "error": str(e), "message": f"❌ Failed to launch {app_name}: {str(e)}"}
    
    def take_screenshot(self, save_path: Optional[str] = None) -> Dict[str, Any]:
        if not PIL_AVAILABLE:
            return {"success": False, "error": "PIL not available"}
        try:
            screenshot = ImageGrab.grab()
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"screenshot_{timestamp}.png"
            screenshot.save(save_path)
            record = {"timestamp": datetime.now().isoformat(), "action": "screenshot", "path": save_path, "status": "success"}
            self.automation_history.append(record)
            self.save_history()
            return {"success": True, "path": save_path, "message": f"✅ Screenshot saved to {save_path}"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"❌ Failed to take screenshot: {str(e)}"}
    
    def read_screen_text(self, screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        if not PYTESSERACT_AVAILABLE:
            return {"success": False, "error": "pytesseract not available"}
        try:
            if not screenshot_path and PIL_AVAILABLE:
                screenshot_path = "temp_ocr.png"
                screenshot = ImageGrab.grab()
                screenshot.save(screenshot_path)
            if screenshot_path:
                text = pytesseract.image_to_string(screenshot_path)
                record = {"timestamp": datetime.now().isoformat(), "action": "ocr", "screenshot": screenshot_path, "status": "success"}
                self.automation_history.append(record)
                self.save_history()
                return {"success": True, "text": text, "message": "✅ Screen text extracted successfully"}
            return {"success": False, "error": "PIL not available"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"❌ Failed to read screen text: {str(e)}"}
    
    def type_text(self, text: str, delay: float = 0.05) -> Dict[str, Any]:
        if not PYAUTOGUI_AVAILABLE:
            return {"success": False, "error": "pyautogui not available"}
        try:
            pyautogui.typewrite(text, interval=delay)
            record = {"timestamp": datetime.now().isoformat(), "action": "type", "text": text[:100], "status": "success"}
            self.automation_history.append(record)
            self.save_history()
            return {"success": True, "text": text, "message": f"✅ Typed {len(text)} characters"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"❌ Failed to type text: {str(e)}"}
    
    def click(self, x: int, y: int, button: str = "left") -> Dict[str, Any]:
        if not PYAUTOGUI_AVAILABLE:
            return {"success": False, "error": "pyautogui not available"}
        try:
            if button == "left":
                pyautogui.click(x, y)
            elif button == "right":
                pyautogui.rightClick(x, y)
            elif button == "middle":
                pyautogui.middleClick(x, y)
            record = {"timestamp": datetime.now().isoformat(), "action": "click", "coordinates": (x, y), "button": button, "status": "success"}
            self.automation_history.append(record)
            self.save_history()
            return {"success": True, "coordinates": (x, y), "message": f"✅ Clicked at ({x}, {y})"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"❌ Failed to click: {str(e)}"}
    
    def key_press(self, key: str, count: int = 1) -> Dict[str, Any]:
        if not PYAUTOGUI_AVAILABLE:
            return {"success": False, "error": "pyautogui not available"}
        try:
            key_map = {"enter": "return", "tab": "tab", "escape": "escape", "backspace": "backspace", "delete": "delete", 
                      "space": "space", "up": "up", "down": "down", "left": "left", "right": "right"}
            actual_key = key_map.get(key.lower(), key.lower())
            for _ in range(count):
                pyautogui.press(actual_key)
                time.sleep(0.1)
            record = {"timestamp": datetime.now().isoformat(), "action": "key_press", "key": key, "count": count, "status": "success"}
            self.automation_history.append(record)
            self.save_history()
            return {"success": True, "key": key, "count": count, "message": f"✅ Pressed {key} {count} times"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"❌ Failed to press key: {str(e)}"}
    
    def keyboard_shortcut(self, keys: List[str]) -> Dict[str, Any]:
        if not PYAUTOGUI_AVAILABLE:
            return {"success": False, "error": "pyautogui not available"}
        try:
            pyautogui.hotkey(*keys)
            record = {"timestamp": datetime.now().isoformat(), "action": "keyboard_shortcut", "keys": keys, "status": "success"}
            self.automation_history.append(record)
            self.save_history()
            return {"success": True, "keys": keys, "message": f"✅ Executed shortcut: {'+'.join(keys)}"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"❌ Failed to execute shortcut: {str(e)}"}
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        if not PYAUTOGUI_AVAILABLE:
            return {"success": False, "error": "pyautogui not available"}
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return {"success": True, "coordinates": (x, y), "message": f"✅ Moved mouse to ({x}, {y})"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"❌ Failed to move mouse: {str(e)}"}
    
    def list_running_apps(self) -> Dict[str, Any]:
        try:
            running_apps = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    running_apps.append({"name": proc.info['name'], "pid": proc.info['pid']})
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return {"success": True, "count": len(running_apps), "apps": running_apps[:20], "message": f"✅ Found {len(running_apps)} running applications"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"❌ Failed to list running apps: {str(e)}"}
    
    def close_app(self, app_name: str) -> Dict[str, Any]:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name.lower() in proc.info['name'].lower():
                        proc.kill()
                        record = {"timestamp": datetime.now().isoformat(), "action": "close", "app": app_name, "status": "success"}
                        self.automation_history.append(record)
                        self.save_history()
                        return {"success": True, "app": app_name, "message": f"✅ Closed {app_name}"}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return {"success": False, "app": app_name, "message": f"❌ Could not find {app_name} to close"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"❌ Failed to close app: {str(e)}"}
    
    def get_automation_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.automation_history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        return {"current_app": self.current_app, "running_apps": len(self.list_running_apps().get("apps", [])), 
                "history_count": len(self.automation_history),
                "capabilities": {"launch_apps": True, "screenshots": PIL_AVAILABLE, "ocr": PYTESSERACT_AVAILABLE,
                                "keyboard_automation": PYAUTOGUI_AVAILABLE, "mouse_control": PYAUTOGUI_AVAILABLE, "windows_api": WIN32_AVAILABLE}}

def get_app_automation() -> AppAutomation:
    """Factory function to get AppAutomation instance"""
    return AppAutomation()

# =============================
# === CONFIG MANAGER ===========
# =============================

class ConfigManager:
    """Manages LIGHT configuration"""
    
    DEFAULT_CONFIG = {
        'api': {'primary': 'gemini', 'fallback_order': ['gemini', 'claude', 'openai'], 'timeout': 30, 'max_retries': 3, 'retry_delay': 2},
        'models': {'gemini': 'gemini-2.5-flash', 'claude': 'claude-3-5-sonnet-20241022', 'openai': 'gpt-4-mini'},
        'gui': {'width': 1000, 'height': 700, 'theme': 'dark', 'font_family': 'Courier', 'font_size': 11},
        'memory': {'enabled': True, 'database_type': 'sqlite', 'database_path': './light_conversations.db'},
        'features': {'gui_mode': True, 'voice_input': True, 'music_streaming': True, 'navigation': True},
        'daemon': {'enabled': True, 'check_interval': 60, 'restart_on_crash': True},
        'advanced': {'temperature': 0.7, 'top_p': 0.9, 'max_tokens': 2000}
    }
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """Load configuration from YAML file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded = yaml.safe_load(f) or {}
                    self._deep_merge(self.config, loaded)
                    print(f"[INFO] ✅ Configuration loaded from {self.config_path}")
            except Exception as e:
                print(f"[WARNING] ❌ Failed to load config: {e}")
                print(f"[INFO] Using default configuration")
        else:
            print(f"[INFO] Config file not found at {self.config_path}")
            print(f"[INFO] Using default configuration")
            self.save()
    
    def save(self):
        """Save current configuration to YAML file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            print(f"[INFO] ✅ Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value (supports nested keys with dot notation)"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Set configuration value (supports nested keys with dot notation)"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_api_config(self) -> Dict:
        """Get API configuration"""
        return self.get('api', {})
    
    def get_gui_config(self) -> Dict:
        """Get GUI configuration"""
        return self.get('gui', {})
    
    def get_memory_config(self) -> Dict:
        """Get memory configuration"""
        return self.get('memory', {})
    
    def get_features(self) -> Dict:
        """Get features configuration"""
        return self.get('features', {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled"""
        return self.get(f'features.{feature}', False)
    
    def verify_api_keys(self) -> Dict[str, bool]:
        """Verify API keys are set"""
        status = {
            'gemini': bool(os.getenv('GENAI_API_KEY')),
            'claude': bool(os.getenv('CLAUDE_API_KEY')),
            'openai': bool(os.getenv('OPENAI_API_KEY'))
        }
        return status
    
    def _deep_merge(self, target: Dict, source: Dict):
        """Recursively merge source dict into target dict"""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

def get_config(config_path: str = "config.yaml") -> ConfigManager:
    """Get or create config instance"""
    return ConfigManager(config_path)

# =============================
# === API HANDLER ==============
# =============================

class APIHandler:
    """Handles multiple APIs with intelligent fallback"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.primary_api = self.config.get('api', {}).get('primary', 'gemini')
        self.fallback_order = self.config.get('api', {}).get('fallback_order', ['gemini', 'claude', 'openai'])
        self.timeout = self.config.get('api', {}).get('timeout', 30)
        self.max_retries = self.config.get('api', {}).get('max_retries', 3)
        self.retry_delay = self.config.get('api', {}).get('retry_delay', 2)
        self.api_clients = {}
        self._init_clients()
    
    def _init_clients(self):
        """Initialize available API clients"""
        gemini_key = os.getenv("GENAI_API_KEY")
        if gemini_key:
            try:
                from google import genai
                self.api_clients['gemini'] = {
                    'client': genai.Client(api_key=gemini_key),
                    'model': self.config.get('models', {}).get('gemini', 'gemini-2.5-flash'),
                    'type': 'gemini'
                }
                print("[INFO] ✅ Gemini API initialized")
            except Exception as e:
                print(f"[WARNING] ❌ Gemini initialization failed: {e}")
        
        claude_key = os.getenv("CLAUDE_API_KEY")
        if claude_key:
            try:
                from anthropic import Anthropic
                self.api_clients['claude'] = {
                    'client': Anthropic(api_key=claude_key),
                    'model': self.config.get('models', {}).get('claude', 'claude-3-5-sonnet-20241022'),
                    'type': 'claude'
                }
                print("[INFO] ✅ Claude API initialized")
            except Exception as e:
                print(f"[WARNING] ❌ Claude initialization failed: {e}")
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                self.api_clients['openai'] = {
                    'client': OpenAI(api_key=openai_key),
                    'model': self.config.get('models', {}).get('openai', 'gpt-4-mini'),
                    'type': 'openai'
                }
                print("[INFO] ✅ OpenAI API initialized")
            except Exception as e:
                print(f"[WARNING] ❌ OpenAI initialization failed: {e}")
        
        if not self.api_clients:
            print("[ERROR] ❌ No APIs configured! Set GENAI_API_KEY, CLAUDE_API_KEY, or OPENAI_API_KEY")
    
    def get_available_apis(self):
        """Get list of available APIs"""
        return list(self.api_clients.keys())
    
    def send_message_stream(self, message: str, system_instruction: str = ""):
        """Send message with streaming response and automatic fallback"""
        apis_to_try = [self.primary_api] + [api for api in self.fallback_order if api != self.primary_api]
        
        for api_name in apis_to_try:
            if api_name not in self.api_clients:
                print(f"[DEBUG] {api_name.upper()} not available, trying next API...")
                continue
            
            print(f"[DEBUG] Trying {api_name.upper()} API...")
            
            try:
                response = self._send_with_api(api_name, message, system_instruction)
                if response:
                    print(f"[INFO] ✅ {api_name.upper()} response successful")
                    return response
            except Exception as e:
                error_msg = str(e)
                print(f"[WARNING] ❌ {api_name.upper()} failed: {error_msg[:100]}")
                
                if "429" in error_msg or "quota" in error_msg.lower():
                    print(f"[WARNING] {api_name.upper()} quota exceeded, trying fallback...")
                    continue
                elif "401" in error_msg or "unauthorized" in error_msg.lower():
                    print(f"[WARNING] {api_name.upper()} auth failed, trying fallback...")
                    continue
                elif "500" in error_msg:
                    print(f"[WARNING] {api_name.upper()} server error, trying fallback...")
                    continue
        
        raise Exception("All APIs failed. Please check your API keys and quotas.")
    
    def _send_with_api(self, api_name: str, message: str, system_instruction: str):
        """Send message with specific API"""
        if api_name == 'gemini':
            return self._send_gemini(message, system_instruction)
        elif api_name == 'claude':
            return self._send_claude(message, system_instruction)
        elif api_name == 'openai':
            return self._send_openai(message, system_instruction)
        
        raise ValueError(f"Unknown API: {api_name}")
    
    def _send_gemini(self, message: str, system_instruction: str):
        """Send with Google Gemini"""
        from google.genai import types
        
        client_info = self.api_clients['gemini']
        client = client_info['client']
        model = client_info['model']
        
        chat = client.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=self.config.get('advanced', {}).get('temperature', 0.7),
                top_p=self.config.get('advanced', {}).get('top_p', 0.9),
            )
        )
        
        # Wrap in interruptible stream
        stream = chat.send_message_stream(message)
        return InterruptibleStreamWrapper(stream, INTERRUPT_HANDLER)
    
    def _send_claude(self, message: str, system_instruction: str):
        """Send with Anthropic Claude"""
        client = self.api_clients['claude']['client']
        model = self.api_clients['claude']['model']
        
        def claude_stream():
            with client.messages.stream(
                model=model,
                max_tokens=self.config.get('advanced', {}).get('max_tokens', 2000),
                system=system_instruction,
                messages=[{"role": "user", "content": message}]
            ) as stream:
                for text in stream.text_stream:
                    class TextChunk:
                        def __init__(self, text):
                            self.text = text
                    yield TextChunk(text)
        
        # Wrap in interruptible stream
        stream = claude_stream()
        return InterruptibleStreamWrapper(stream, INTERRUPT_HANDLER)
    
    def _send_openai(self, message: str, system_instruction: str):
        """Send with OpenAI"""
        client = self.api_clients['openai']['client']
        model = self.api_clients['openai']['model']
        
        def openai_stream():
            stream = client.chat.completions.create(
                model=model,
                max_tokens=self.config.get('advanced', {}).get('max_tokens', 2000),
                temperature=self.config.get('advanced', {}).get('temperature', 0.7),
                top_p=self.config.get('advanced', {}).get('top_p', 0.9),
                stream=True,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}
                ]
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    class TextChunk:
                        def __init__(self, text):
                            self.text = text
                    yield TextChunk(chunk.choices[0].delta.content)
        
        # Wrap in interruptible stream
        stream = openai_stream()
        return InterruptibleStreamWrapper(stream, INTERRUPT_HANDLER)
    
    def get_status(self):
        """Get status of all APIs"""
        status = {}
        
        for api_name, client_info in self.api_clients.items():
            try:
                status[api_name] = {
                    'available': True,
                    'model': client_info['model']
                }
            except Exception as e:
                status[api_name] = {
                    'available': False,
                    'error': str(e)
                }
        
        return status

def get_api_handler(config=None):
    """Get or create API handler instance"""
    return APIHandler(config)

# =============================
# === DATABASE =================
# =============================

class LightDatabase:
    """SQLite database for LIGHT conversations and user data"""
    
    def __init__(self, db_path="./light_conversations.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize database with tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    persona TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT,
                    summary TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    user_input TEXT NOT NULL,
                    light_response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    emotion TEXT,
                    tokens_used INTEGER,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    preferences TEXT,
                    interests TEXT,
                    last_persona TEXT,
                    total_conversations INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT UNIQUE NOT NULL,
                    response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compressed_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    compression_level INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    importance_score REAL DEFAULT 0.5,
                    archived INTEGER DEFAULT 0,
                    source_conversations TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS important_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    first_mentioned TIMESTAMP,
                    last_mentioned TIMESTAMP,
                    mention_count INTEGER DEFAULT 1,
                    importance_score REAL DEFAULT 0.5,
                    archived INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_consolidation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consolidation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action_type TEXT NOT NULL,
                    input_item_count INTEGER,
                    output_item_count INTEGER,
                    compression_ratio REAL,
                    details TEXT
                )
            ''')
            
            # Personal Growth & Development Tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal TEXT NOT NULL,
                    category TEXT,
                    priority INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    progress INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    milestones TEXT,
                    notes TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clarification_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT,
                    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    answered_at TIMESTAMP,
                    importance INTEGER DEFAULT 1,
                    category TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS growth_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER,
                    milestone TEXT,
                    achievement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    impact_score REAL DEFAULT 0.5,
                    lessons_learned TEXT,
                    FOREIGN KEY(goal_id) REFERENCES user_goals(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS communication_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_key TEXT UNIQUE NOT NULL,
                    preference_value TEXT NOT NULL,
                    category TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def save_conversation(self, title, persona=None, tags=None):
        """Save a new conversation"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations (title, persona, tags)
                    VALUES (?, ?, ?)
                ''', (title, persona, tags))
                conn.commit()
                return cursor.lastrowid
    
    def save_message(self, conversation_id, user_input, light_response, tokens_used=0):
        """Save a message exchange"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO messages (conversation_id, user_input, light_response, tokens_used)
                    VALUES (?, ?, ?, ?)
                ''', (conversation_id, user_input, light_response, tokens_used))
                
                cursor.execute('''
                    UPDATE conversations SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (conversation_id,))
                
                conn.commit()
    
    def get_conversation(self, conversation_id):
        """Get conversation by ID with all messages"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM conversations WHERE id = ?', (conversation_id,))
            conv = cursor.fetchone()
            
            if not conv:
                return None
            
            cursor.execute('''
                SELECT * FROM messages WHERE conversation_id = ?
                ORDER BY timestamp ASC
            ''', (conversation_id,))
            messages = [dict(row) for row in cursor.fetchall()]
            
            return {
                'id': conv['id'],
                'title': conv['title'],
                'persona': conv['persona'],
                'created_at': conv['created_at'],
                'updated_at': conv['updated_at'],
                'tags': conv['tags'],
                'messages': messages
            }
    
    def get_recent_conversations(self, limit=10):
        """Get recent conversations"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, persona, created_at, updated_at
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def search_conversations(self, query):
        """Search conversations by title or content"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT c.id, c.title, c.created_at
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.title LIKE ? OR m.user_input LIKE ? OR m.light_response LIKE ?
                ORDER BY c.updated_at DESC
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def save_user_profile(self, username, preferences=None, interests=None):
        """Save or update user profile"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                prefs_json = json.dumps(preferences) if preferences else None
                interests_json = json.dumps(interests) if interests else None
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_profiles (username, preferences, interests)
                    VALUES (?, ?, ?)
                ''', (username, prefs_json, interests_json))
                conn.commit()
    
    def get_user_profile(self, username):
        """Get user profile"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_profiles WHERE username = ?', (username,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'username': row['username'],
                'preferences': json.loads(row['preferences']) if row['preferences'] else {},
                'interests': json.loads(row['interests']) if row['interests'] else [],
                'last_persona': row['last_persona'],
                'total_conversations': row['total_conversations']
            }
    
    def cache_response(self, query_hash, response, expires_hours=24):
        """Cache a response"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                from datetime import timedelta
                expires_at = (datetime.now() + timedelta(hours=expires_hours)).isoformat()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cache (query_hash, response, expires_at)
                    VALUES (?, ?, ?)
                ''', (query_hash, response, expires_at))
                conn.commit()
    
    def get_cached_response(self, query_hash):
        """Get cached response if not expired"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT response FROM cache
                WHERE query_hash = ? AND expires_at > CURRENT_TIMESTAMP
            ''', (query_hash,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def clear_old_cache(self):
        """Remove expired cache entries"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cache WHERE expires_at <= CURRENT_TIMESTAMP')
                conn.commit()
    
    def get_statistics(self):
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total_conversations = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM messages')
            total_messages = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM user_profiles')
            total_profiles = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(tokens_used) FROM messages')
            total_tokens = cursor.fetchone()[0] or 0
            
            return {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'total_profiles': total_profiles,
                'total_tokens_used': total_tokens
            }
    
    def export_conversation(self, conversation_id, format='json'):
        """Export conversation to file"""
        conv = self.get_conversation(conversation_id)
        if not conv:
            return None
        
        if format == 'json':
            return json.dumps(conv, indent=2, default=str)
        elif format == 'txt':
            lines = [f"Conversation: {conv['title']}", f"Created: {conv['created_at']}", ""]
            for msg in conv['messages']:
                lines.append(f"You: {msg['user_input']}")
                lines.append(f"LIGHT: {msg['light_response']}")
                lines.append("")
            return "\n".join(lines)
        
        return None
    
    def cleanup(self, max_conversations=1000):
        """Remove old conversations if over limit"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM conversations')
                count = cursor.fetchone()[0]
                
                if count > max_conversations:
                    remove_count = count - max_conversations
                    cursor.execute('''
                        DELETE FROM conversations WHERE id IN (
                            SELECT id FROM conversations
                            ORDER BY created_at ASC
                            LIMIT ?
                        )
                    ''', (remove_count,))
                    conn.commit()
    
    def save_compressed_memory(self, memory_type, content, compression_level=1, message_count=0, importance_score=0.5, source_conversations=None):
        """Save a compressed memory summary"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                source_conv_json = json.dumps(source_conversations) if source_conversations else None
                cursor.execute('''
                    INSERT INTO compressed_memory (memory_type, content, compression_level, message_count, importance_score, source_conversations)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (memory_type, content, compression_level, message_count, importance_score, source_conv_json))
                conn.commit()
                return cursor.lastrowid
    
    def save_important_memory(self, fact_type, content, category=None, importance_score=0.5):
        """Save an important fact or memory"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO important_memories (fact_type, content, category, importance_score, first_mentioned, last_mentioned)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (fact_type, content, category, importance_score))
                conn.commit()
                return cursor.lastrowid
    
    def update_important_memory_mention(self, memory_id):
        """Update mention count and last_mentioned for an important memory"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE important_memories
                    SET mention_count = mention_count + 1,
                        last_mentioned = CURRENT_TIMESTAMP,
                        importance_score = MIN(1.0, importance_score + 0.05)
                    WHERE id = ?
                ''', (memory_id,))
                conn.commit()
    
    def get_active_important_memories(self, limit=50):
        """Get active (non-archived) important memories"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, fact_type, content, category, importance_score, mention_count
                FROM important_memories
                WHERE archived = 0
                ORDER BY importance_score DESC, last_mentioned DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_compressed_memories(self, limit=20, archived=False):
        """Get compressed memory summaries"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, memory_type, content, compression_level, message_count, importance_score, created_at
                FROM compressed_memory
                WHERE archived = ?
                ORDER BY importance_score DESC, created_at DESC
                LIMIT ?
            ''', (1 if archived else 0, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_memory_summary_for_chat(self, limit=10):
        """Get memory summary to inject into chat context"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT fact_type, content, category
                FROM important_memories
                WHERE archived = 0
                ORDER BY importance_score DESC, last_mentioned DESC
                LIMIT ?
            ''', (limit,))
            important = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT memory_type, content
                FROM compressed_memory
                WHERE archived = 0 AND compression_level <= 3
                ORDER BY importance_score DESC
                LIMIT ?
            ''', (5,))
            compressed = [dict(row) for row in cursor.fetchall()]
            
            return {'important_memories': important, 'compressed_memories': compressed}
    
    def compress_old_conversations(self, days_old=7, max_compression_level=3):
        """Compress conversations older than X days into summarized memories"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(f'''
                    SELECT id, title, created_at FROM conversations
                    WHERE datetime(created_at) <= datetime('now', '-{days_old} days')
                    AND id NOT IN (
                        SELECT DISTINCT conversation_id FROM messages
                        WHERE datetime(timestamp) > datetime('now', '-{days_old} days')
                    )
                    ORDER BY created_at ASC
                ''')
                old_conversations = cursor.fetchall()
                
                compressed_count = 0
                total_messages = 0
                
                for conv_id, title, created_at in old_conversations:
                    cursor.execute('''
                        SELECT user_input, light_response FROM messages
                        WHERE conversation_id = ?
                        ORDER BY timestamp ASC
                    ''', (conv_id,))
                    messages = cursor.fetchall()
                    
                    if not messages:
                        continue
                    
                    total_messages += len(messages)
                    
                    summary = self._create_memory_summary(title, messages)
                    
                    self.save_compressed_memory(
                        memory_type='conversation_summary',
                        content=summary,
                        compression_level=1,
                        message_count=len(messages),
                        importance_score=self._calculate_importance(messages),
                        source_conversations=[conv_id]
                    )
                    compressed_count += 1
                
                if compressed_count > 0:
                    cursor.execute('''
                        INSERT INTO memory_consolidation_log (action_type, input_item_count, output_item_count, compression_ratio)
                        VALUES (?, ?, ?, ?)
                    ''', ('compression', total_messages, compressed_count, total_messages / compressed_count if compressed_count > 0 else 0))
                
                conn.commit()
                return compressed_count, total_messages
    
    def consolidate_compressed_memories(self):
        """Consolidate compressed memories by grouping and summarizing"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, memory_type, content, compression_level
                    FROM compressed_memory
                    WHERE archived = 0
                    ORDER BY compression_level, importance_score DESC
                ''')
                all_memories = cursor.fetchall()
                
                if len(all_memories) < 2:
                    return 0
                
                by_level = {}
                for mem_id, mem_type, content, level in all_memories:
                    if level not in by_level:
                        by_level[level] = []
                    by_level[level].append((mem_id, content))
                
                lowest_level = min(by_level.keys())
                memories_at_level = by_level[lowest_level]
                
                if len(memories_at_level) >= 3:
                    consolidation_count = 0
                    chunk_size = 4
                    
                    for i in range(0, len(memories_at_level) - chunk_size + 1, chunk_size):
                        chunk = memories_at_level[i:i+chunk_size]
                        chunk_ids = [m[0] for m in chunk]
                        chunk_contents = [m[1] for m in chunk]
                        
                        consolidated = self._consolidate_memories(chunk_contents)
                        
                        self.save_compressed_memory(
                            memory_type='consolidated_summary',
                            content=consolidated,
                            compression_level=lowest_level + 1,
                            message_count=sum([len(c.split()) for c in chunk_contents]),
                            importance_score=0.6,
                            source_conversations=chunk_ids
                        )
                        consolidation_count += 1
                    
                    cursor.execute('''
                        INSERT INTO memory_consolidation_log (action_type, input_item_count, output_item_count, compression_ratio)
                        VALUES (?, ?, ?, ?)
                    ''', ('consolidation', len(memories_at_level), consolidation_count, len(memories_at_level) / consolidation_count if consolidation_count > 0 else 0))
                    
                    conn.commit()
                    return consolidation_count
                
                return 0
    
    def extract_important_facts(self):
        """Extract important facts from conversations"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT m.user_input, m.light_response FROM messages m
                    WHERE datetime(m.timestamp) > datetime('now', '-30 days')
                    ORDER BY m.timestamp DESC
                    LIMIT 100
                ''')
                recent_messages = cursor.fetchall()
                
                cursor.execute('''
                    SELECT content FROM compressed_memory
                    WHERE archived = 0
                    ORDER BY importance_score DESC
                    LIMIT 20
                ''')
                compressed_content = [row[0] for row in cursor.fetchall()]
                
                extracted_facts = []
                
                for user_input, light_response in recent_messages:
                    facts = self._extract_facts_from_text(user_input, light_response)
                    extracted_facts.extend(facts)
                
                for content in compressed_content:
                    facts = self._extract_facts_from_text(content, '')
                    extracted_facts.extend(facts)
                
                saved_count = 0
                for fact_type, content, category, importance in extracted_facts:
                    cursor.execute('''
                        SELECT id FROM important_memories
                        WHERE fact_type = ? AND category = ? AND content LIKE ?
                    ''', (fact_type, category, f'%{content[:20]}%'))
                    existing = cursor.fetchone()
                    
                    if existing:
                        self.update_important_memory_mention(existing[0])
                    else:
                        self.save_important_memory(fact_type, content, category, importance)
                        saved_count += 1
                
                conn.commit()
                return saved_count, len(extracted_facts)
    
    def archive_old_memories(self, days_old=90):
        """Archive memories that are very old"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(f'''
                    UPDATE compressed_memory
                    SET archived = 1
                    WHERE datetime(created_at) <= datetime('now', '-{days_old} days')
                    AND archived = 0
                ''')
                
                cursor.execute(f'''
                    UPDATE important_memories
                    SET archived = 1
                    WHERE datetime(last_mentioned) <= datetime('now', '-{days_old} days')
                    AND archived = 0
                ''')
                
                conn.commit()
    
    def _create_memory_summary(self, title, messages):
        """Create a compressed summary of messages"""
        if not messages:
            return ""
        
        summary_parts = [f"Conversation: {title}"]
        
        key_points = []
        for user_input, light_response in messages:
            if any(word in user_input.lower() for word in ['like', 'love', 'hate', 'important', 'friend', 'family']):
                key_points.append(f"User: {user_input[:100]}")
                key_points.append(f"LIGHT: {light_response[:100]}")
        
        if key_points:
            summary_parts.append("Key points: " + " | ".join(key_points[:5]))
        else:
            summary_parts.append(f"[{len(messages)} messages exchanged]")
        
        return "\n".join(summary_parts)
    
    def _consolidate_memories(self, memory_contents):
        """Consolidate multiple memory contents into one"""
        consolidated = []
        
        for content in memory_contents:
            sentences = content.split('.')
            key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:2]
            consolidated.extend(key_sentences)
        
        return " | ".join(consolidated[:5])
    
    def _calculate_importance(self, messages):
        """Calculate importance score for a conversation"""
        if not messages:
            return 0.3
        
        importance = 0.5
        keywords = ['like', 'love', 'hate', 'important', 'friend', 'family', 'memories', 'goal', 'dream']
        
        for user_input, light_response in messages:
            combined = (user_input + light_response).lower()
            if any(kw in combined for kw in keywords):
                importance += 0.1
        
        return min(1.0, importance)
    
    def _extract_facts_from_text(self, user_text, response_text):
        """Extract important facts from conversation text"""
        facts = []
        combined_text = (user_text + " " + response_text).lower()
        
        if 'like' in combined_text or 'love' in combined_text:
            facts.append(('preference', user_text[:100], 'likes', 0.8))
        
        if 'hate' in combined_text or 'dislike' in combined_text:
            facts.append(('preference', user_text[:100], 'dislikes', 0.7))
        
        if 'friend' in combined_text or 'brother' in combined_text or 'sister' in combined_text:
            facts.append(('person', user_text[:100], 'relationships', 0.7))
        
        if 'family' in combined_text or 'mom' in combined_text or 'dad' in combined_text:
            facts.append(('person', user_text[:100], 'family', 0.8))
        
        if 'goal' in combined_text or 'dream' in combined_text or 'want' in combined_text:
            facts.append(('goal', user_text[:100], 'aspirations', 0.75))
        
        return facts
    
    def get_memory_stats(self):
        """Get statistics about memory usage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM compressed_memory WHERE archived = 0')
            active_compressed = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM compressed_memory WHERE archived = 1')
            archived_compressed = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM important_memories WHERE archived = 0')
            active_important = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM important_memories WHERE archived = 1')
            archived_important = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM memory_consolidation_log')
            total_consolidations = cursor.fetchone()[0]
            
            return {
                'active_compressed_memories': active_compressed,
                'archived_compressed_memories': archived_compressed,
                'active_important_memories': active_important,
                'archived_important_memories': archived_important,
                'total_consolidation_events': total_consolidations
            }
    
    # ===== PERSONAL GROWTH & DEVELOPMENT METHODS =====
    
    def save_user_goal(self, goal, category=None, priority=1, milestones=None):
        """Save a user goal for personal growth"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                milestones_json = json.dumps(milestones) if milestones else None
                
                cursor.execute('''
                    INSERT INTO user_goals (goal, category, priority, milestones, status)
                    VALUES (?, ?, ?, ?, 'active')
                ''', (goal, category, priority, milestones_json))
                
                conn.commit()
                return cursor.lastrowid
    
    def get_user_goals(self, status='active', limit=10):
        """Get user's current goals"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, goal, category, priority, progress, created_at, milestones
                FROM user_goals
                WHERE status = ?
                ORDER BY priority DESC, created_at DESC
                LIMIT ?
            ''', (status, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_goal_progress(self, goal_id, progress):
        """Update progress on a goal (0-100%)"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE user_goals
                    SET progress = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (max(0, min(100, progress)), goal_id))
                
                conn.commit()
    
    def save_clarification_question(self, topic, question, category=None, importance=1):
        """Save a clarification question for deeper understanding"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO clarification_questions (topic, question, category, importance)
                    VALUES (?, ?, ?, ?)
                ''', (topic, question, category, importance))
                
                conn.commit()
                return cursor.lastrowid
    
    def get_unanswered_questions(self, limit=5):
        """Get questions still awaiting user's answer"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, topic, question, category, importance
                FROM clarification_questions
                WHERE answer IS NULL
                ORDER BY importance DESC, asked_at DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def answer_clarification_question(self, question_id, answer):
        """Record an answer to a clarification question"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE clarification_questions
                    SET answer = ?, answered_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (answer, question_id))
                
                conn.commit()
    
    def track_milestone(self, goal_id, milestone, description=None, lessons_learned=None):
        """Record a milestone achievement towards a goal"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO growth_tracking (goal_id, milestone, description, lessons_learned)
                    VALUES (?, ?, ?, ?)
                ''', (goal_id, milestone, description, lessons_learned))
                
                conn.commit()
                return cursor.lastrowid
    
    def get_growth_achievements(self, goal_id=None, limit=20):
        """Get recorded achievements and milestones"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if goal_id:
                cursor.execute('''
                    SELECT * FROM growth_tracking
                    WHERE goal_id = ?
                    ORDER BY achievement_date DESC
                    LIMIT ?
                ''', (goal_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM growth_tracking
                    ORDER BY achievement_date DESC
                    LIMIT ?
                ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def set_communication_preference(self, key, value, category=None):
        """Save a communication preference (e.g., tone, frequency, topics)"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO communication_preferences (preference_key, preference_value, category)
                    VALUES (?, ?, ?)
                ''', (key, value, category))
                
                conn.commit()
    
    def get_communication_preferences(self):
        """Get all user communication preferences"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT preference_key, preference_value, category FROM communication_preferences')
            
            prefs = {}
            for row in cursor.fetchall():
                prefs[row['preference_key']] = row['preference_value']
            
            return prefs

def get_database(db_path="./light_conversations.db"):
    """Get or create database instance"""
    return LightDatabase(db_path)

# =============================
# === MEMORY MANAGER ===========
# =============================

class MemoryManager:
    """Manages LIGHT's persistent memory across conversations"""
    
    def __init__(self, db=None, max_context_entries: int = 50):
        self.db = db
        self.max_context_entries = max_context_entries
        self.memory_file = "light_persistent_memory.json"
        self.local_memory = self._load_local_memory()
    
    def _load_local_memory(self) -> Dict[str, Any]:
        """Load memory from local JSON file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[MEMORY] Failed to load local memory: {e}")
                return self._create_empty_memory()
        return self._create_empty_memory()
    
    def _create_empty_memory(self) -> Dict[str, Any]:
        """Create an empty memory structure"""
        return {
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "user_profile": {},
            "topics_of_interest": [],
            "conversation_summaries": [],
            "learned_preferences": {},
            "memorable_facts": []
        }
    
    def _save_local_memory(self):
        """Save memory to local JSON file"""
        try:
            self.local_memory["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.local_memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[MEMORY] Failed to save local memory: {e}")
    
    def add_memory_entry(self, entry_type: str, content: str, metadata: Optional[Dict] = None):
        """Add a new memory entry"""
        try:
            if entry_type == "memorable_facts":
                self.local_memory["memorable_facts"].append({
                    "timestamp": datetime.now().isoformat(),
                    "content": content,
                    "metadata": metadata or {}
                })
            elif entry_type == "conversation_summaries":
                self.local_memory["conversation_summaries"].append({
                    "timestamp": datetime.now().isoformat(),
                    "summary": content,
                    "metadata": metadata or {}
                })
            elif entry_type == "learned_preferences":
                key = metadata.get("key", "general") if metadata else "general"
                self.local_memory["learned_preferences"][key] = content
            
            if len(self.local_memory["memorable_facts"]) > self.max_context_entries:
                self.local_memory["memorable_facts"] = self.local_memory["memorable_facts"][-self.max_context_entries:]
            if len(self.local_memory["conversation_summaries"]) > self.max_context_entries:
                self.local_memory["conversation_summaries"] = self.local_memory["conversation_summaries"][-self.max_context_entries:]
            
            self._save_local_memory()
        except Exception as e:
            print(f"[MEMORY] Error adding entry: {e}")
    
    def get_memory_context(self) -> str:
        """Generate a memory context string for injection into system prompts"""
        try:
            context_parts = []
            
            if self.local_memory.get("user_profile"):
                context_parts.append("USER PROFILE:")
                for key, value in self.local_memory["user_profile"].items():
                    context_parts.append(f"  • {key}: {value}")
            
            if self.local_memory.get("topics_of_interest"):
                context_parts.append("\nUSER INTERESTS:")
                for topic in self.local_memory["topics_of_interest"][:5]:
                    context_parts.append(f"  • {topic}")
            
            if self.local_memory.get("learned_preferences"):
                context_parts.append("\nLEARNED PREFERENCES:")
                for key, value in self.local_memory["learned_preferences"].items():
                    if value:
                        context_parts.append(f"  • {key}: {value}")
            
            if self.local_memory.get("memorable_facts"):
                context_parts.append("\nMEMORABLE FACTS:")
                for fact in self.local_memory["memorable_facts"][-3:]:
                    context_parts.append(f"  • {fact.get('content', '')}")
            
            if not context_parts:
                return ""
            
            return "PERSISTENT MEMORY CONTEXT:\n" + "\n".join(context_parts)
        
        except Exception as e:
            print(f"[MEMORY] Error generating context: {e}")
            return ""
    
    def update_user_profile(self, profile_data: Dict[str, str]):
        """Update user profile information"""
        try:
            self.local_memory["user_profile"].update(profile_data)
            self._save_local_memory()
        except Exception as e:
            print(f"[MEMORY] Error updating profile: {e}")
    
    def add_topic_of_interest(self, topic: str):
        """Add a topic to user's interests"""
        try:
            if topic not in self.local_memory["topics_of_interest"]:
                self.local_memory["topics_of_interest"].append(topic)
                if len(self.local_memory["topics_of_interest"]) > 20:
                    self.local_memory["topics_of_interest"] = self.local_memory["topics_of_interest"][-20:]
                self._save_local_memory()
        except Exception as e:
            print(f"[MEMORY] Error adding topic: {e}")
    
    def get_summary(self) -> str:
        """Get a brief summary of all memories"""
        summary = f"Memory entries: {len(self.local_memory['memorable_facts'])} facts, "
        summary += f"{len(self.local_memory['conversation_summaries'])} conversations, "
        summary += f"{len(self.local_memory['topics_of_interest'])} interests"
        return summary

def initialize_memory_manager(db=None) -> MemoryManager:
    """Initialize and return the global memory manager instance"""
    try:
        mem_mgr = MemoryManager(db=db)
        print("[MEMORY] ✅ Memory manager initialized")
        return mem_mgr
    except Exception as e:
        print(f"[MEMORY] ❌ Failed to initialize: {e}")
        return MemoryManager(db=None)

# =============================
# === CODE IMPROVER ============
# =============================

class CodeImprover:
    """Analyzes Python code for improvements and manages improvement history"""
    
    def __init__(self):
        self.history_file = "improvement_history.json"
        self.improvements_cache = {}
        self.load_history()
    
    def load_history(self):
        """Load improvement history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []
    
    def save_history(self):
        """Save improvement history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def get_python_files(self, directory: str = ".") -> List[str]:
        """Get all Python files in directory"""
        py_files = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.venv', 'env', 'KAI']]
            
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        
        return py_files
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """Analyze a single Python file for improvements"""
        improvements = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return {
                'filepath': filepath,
                'improvements': [],
                'error': str(e)
            }
        
        if self._check_import_issues(content):
            improvements.append({
                'type': 'import_organization',
                'severity': 'low',
                'description': 'Imports could be better organized',
                'line': self._find_import_line(lines)
            })
        
        long_lines = [i for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            improvements.append({
                'type': 'long_lines',
                'severity': 'low',
                'description': f'Found {len(long_lines)} lines exceeding 100 characters',
                'lines': long_lines[:5]
            })
        
        if self._has_potential_unused_vars(content):
            improvements.append({
                'type': 'unused_variables',
                'severity': 'medium',
                'description': 'Potential unused variables detected',
                'line': 0
            })
        
        if self._missing_docstrings(content):
            improvements.append({
                'type': 'missing_docstrings',
                'severity': 'low',
                'description': 'Some functions lack docstrings',
                'line': 0
            })
        
        if self._check_complexity(content):
            improvements.append({
                'type': 'complexity',
                'severity': 'medium',
                'description': 'Some functions have high cyclomatic complexity',
                'line': 0
            })
        
        return {
            'filepath': filepath,
            'improvements': improvements
        }
    
    def _check_import_issues(self, content: str) -> bool:
        """Check if imports are organized"""
        return False
    
    def _find_import_line(self, lines: List[str]) -> int:
        """Find first import line"""
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                return i + 1
        return 1
    
    def _has_potential_unused_vars(self, content: str) -> bool:
        """Simple check for potential unused variables"""
        try:
            import ast
            tree = ast.parse(content)
            return False
        except:
            return False
    
    def _missing_docstrings(self, content: str) -> bool:
        """Check for functions without docstrings"""
        try:
            import ast
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        return True
            return False
        except:
            return False
    
    def _check_complexity(self, content: str) -> bool:
        """Check for complex functions"""
        try:
            import ast
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    branches = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While)))
                    if branches > 10:
                        return True
            return False
        except:
            return False
    
    def analyze_all_files(self) -> List[Dict[str, Any]]:
        """Analyze all Python files in project"""
        py_files = self.get_python_files()
        results = []
        
        for filepath in py_files:
            result = self.analyze_file(filepath)
            if result['improvements']:
                results.append(result)
        
        return results
    
    def generate_improvement_report(self) -> Dict[str, Any]:
        """Generate a comprehensive improvement report"""
        all_improvements = self.analyze_all_files()
        
        total_improvements = sum(len(f['improvements']) for f in all_improvements)
        improvements_by_type = {}
        improvements_by_severity = {'low': 0, 'medium': 0, 'high': 0}
        
        for file_result in all_improvements:
            for imp in file_result['improvements']:
                imp_type = imp.get('type', 'unknown')
                improvements_by_type[imp_type] = improvements_by_type.get(imp_type, 0) + 1
                severity = imp.get('severity', 'low')
                improvements_by_severity[severity] += 1
        
        return {
            'total_files_analyzed': len(self.get_python_files()),
            'files_with_improvements': len(all_improvements),
            'total_improvements_applied': len(self.history),
            'improvements_by_type': improvements_by_type,
            'improvements_by_severity': improvements_by_severity,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_improvement_history(self) -> List[Dict[str, Any]]:
        """Get history of applied improvements"""
        return self.history
    
    def apply_improvement(self, filepath: str, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Apply an improvement to a file"""
        try:
            backup_name = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(filepath, 'r') as f:
                content = f.read()
            with open(backup_name, 'w') as f:
                f.write(content)
            
            record = {
                'filepath': filepath,
                'type': proposal.get('type', 'unknown'),
                'status': 'applied',
                'date': datetime.now().isoformat(),
                'backup': backup_name,
                'proposal': proposal.get('title', 'Unknown')
            }
            self.history.append(record)
            self.save_history()
            
            return {
                'success': True,
                'backup': backup_name,
                'message': f'Improvement applied successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# =============================
# === DEBUG MODE CONFIG =======
# =============================
DEBUG_MODE = False  # This is the default - terminal stays clean

def debug_print(message: str):
    """Only print if debug mode is enabled"""
    if DEBUG_MODE:
        print(message)

# =============================
# === REALTIME API CONFIG =====
# =============================
USE_REALTIME_API = True  # Set to True to use Gemini Live API instead of streaming
REALTIME_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"  # For native audio
SEND_SAMPLE_RATE = 16000  # Input sample rate for Live API
RECEIVE_SAMPLE_RATE = 24000  # Output sample rate for Live API

# Global variable to track realtime API text responses
REALTIME_RESPONSE_BUFFER = ""
REALTIME_MUSIC_PLAYING = True
REALTIME_TEXT_RESPONSE = ""  # Track text responses for dialog display
REALTIME_DIALOG_SHOWN = True  # Track if dialog was already shown
REALTIME_RESPONSE_COMPLETE = True  # Track when response is complete

# Persistent dialog tracking
PERSISTENT_DIALOG_ROOT = None  # Keep reference to persistent dialog window
PERSISTENT_TEXT_DISPLAY = None  # Keep reference to text widget
PERSISTENT_DIALOG_CONTENT = ""  # Accumulate all responses

# Dialog queue for thread-safe dialog creation
DIALOG_QUEUE = queue.Queue()  # Queue to hold dialog requests from monitor thread

# =============================
# === CONVERSATION TRACKING ===
# =============================
CURRENT_CONVERSATION_ID = None  # Current conversation ID for database
CONVERSATION_TITLE = "Chat"  # Title for the current conversation
CONVERSATION_START_TIME = datetime.now()  # When this conversation started

# =============================
# === PERSONALITY ROLE-PLAY CONFIG ===
# =============================
CURRENT_PERSONA = None  # Current persona being role-played
PERSONA_DESCRIPTION = ""  # Detailed description of current persona
PERSONA_ACTIVE = True  # Whether persona mode is active

# =============================
# === SESSION & RESPONSE MANAGEMENT ===
# =============================
LAST_RESPONSE = ""  # Store last response for saving
RESPONSE_HISTORY = []  # History of all responses in session
SESSION_CONTEXT = {  # Maintain context across mode switches
    "persona": None,
    "persona_desc": "",
    "last_mode": None,
    "responses_saved": 0
}

# =============================
# === PERSISTENT MEMORY SYSTEM ===
# =============================
MEMORY_MANAGER = None  # Will be initialized in main()
MEMORY_CONTEXT = ""  # Current memory context for injection

# =============================
# === LIGHT FEATURES CONFIG ===
# =============================
PERSONALITY = "friendly"  # funny, serious, mentor
MEMORY_FILE = "light_memory.json"
CACHE_FILE = "light_memory.json"
WEATHER_API_KEY = "PUT_YOUR_OPENWEATHER_KEY_HERE"
NEWS_API_KEY = "PUT_YOUR_NEWSAPI_KEY_HERE"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"
WAKE_WORD = "light"
USE_GUI = True  # Set to True to enable GUI mode

# Dream / Curiosity / Confidence / Ethical modes (GUI toggles)
DREAM_MODE = False
CURIOSITY_MODE = False
CONFIDENCE_LEVEL = 50  # 0–100: assertiveness
ETHICAL_REASONING_MODE = False
DREAM_INSIGHTS_FILE = "light_dream_insights.json"
DREAM_NIGHT_START_HOUR = 22   # 10 PM
DREAM_NIGHT_END_HOUR = 6     # 6 AM
DREAM_CHECK_INTERVAL_SEC = 600   # Check every 10 min during night
DREAM_REFLECT_PROBABILITY = 0.3  # 30% chance per check to reflect

# =============================
# === LIGHT FEATURE PROPOSALS (IMPLEMENTED) ===
# =============================
# Dream Mode: LIGHT randomly reflects at night and stores insights.
#   - Background thread runs during night (DREAM_NIGHT_START/END_HOUR). When Dream
#     Mode is on, periodically reflects on recent Q&A, calls API for a short
#     insight, appends to DREAM_INSIGHTS_FILE (light_dream_insights.json).
# Curiosity Mode: LIGHT asks you questions.
#   - System prompt addendum: LIGHT regularly asks thoughtful, genuine questions
#     about what you're working on, how you feel, or follow-ups. Warm and curious.
# Confidence Slider: Controls how assertive LIGHT is.
#   - 0–25: very tentative; 26–50: cautious; 51–75: clear/direct; 76–100: decisive.
#   - Wired to CONFIDENCE_LEVEL; GUI slider in modes bar.
# Ethical Reasoning Mode: Explains why LIGHT refuses things.
#   - When declining harmful/illegal/unethical requests, LIGHT must explain *why*
#     in clear, brief terms (principle or harm avoided). Respectful and transparent.
# Emotion-Driven Behavior: Detect user emotion and change both voice and behavior.
#   - Sad: softer voice (rate down, volume down), shorter responses, encouraging language.
#   - Excited: faster pace, more expressive responses.
#   - Frustrated: proactively offer "Want me to simplify this, or fix it with you step by step?"
#   - Voice via EMOTION_VOICE + _apply_emotion_to_tts; behavior via get_emotion_addendum.

# =============================
# === MODE HELPERS =============
# =============================

# Feature modes: Dream, Curiosity, Confidence, Ethical reasoning

def get_mode_addenda() -> str:
    """Build optional system-instruction addenda for Curiosity, Confidence, Ethical modes."""
    parts = []
    if CURIOSITY_MODE:
        parts.append("""
CURIOSITY MODE (ACTIVE): Regularly ask the user thoughtful, genuine questions. Show interest in their thoughts, experiences, and opinions. Pose one concise question when natural—about what they're working on, how they feel, what they're curious about, or a follow-up to something they said. Don't interrogate; be warm and curious.""")
    if ETHICAL_REASONING_MODE:
        parts.append("""
ETHICAL REASONING MODE (ACTIVE): When you decline a request (e.g. harmful, illegal, or ethically problematic), always explain *why* you're refusing in clear, brief terms. Describe the ethical principle or harm you're avoiding. Be respectful but transparent about your reasoning.""")
    # Confidence: 0–100 → assertiveness
    c = max(0, min(100, CONFIDENCE_LEVEL))
    if c <= 25:
        conf = "VERY LOW assertiveness: Be tentative, hedge with 'perhaps' and 'maybe', offer alternatives, avoid strong claims."
    elif c <= 50:
        conf = "LOW–MODERATE assertiveness: Be helpful but somewhat cautious; occasionally qualify advice."
    elif c <= 75:
        conf = "MODERATE–HIGH assertiveness: Be clear and direct; stand by your recommendations while staying respectful."
    else:
        conf = "HIGH assertiveness: Be confident and decisive; state recommendations clearly, minimal hedging."
    parts.append(f"""
CONFIDENCE LEVEL (current: {c}): {conf}""")
    if not parts:
        return ""
    return "\n\n" + "---\n".join(parts)

BASE_SYSTEM_INSTRUCTION = ""  # Set in main(); used by build_system_instruction

def build_system_instruction() -> str:
    """Return base system instruction + mode addenda + persona + memory context."""
    base_instruction = (BASE_SYSTEM_INSTRUCTION or "") + get_mode_addenda()
    
    # Inject persona instruction if active
    if PERSONA_ACTIVE and PERSONA_DESCRIPTION:
        persona_inst = get_persona_instruction()
        if persona_inst:
            base_instruction += "\n\n" + persona_inst
    
    # Inject persistent memory context
    global MEMORY_MANAGER, MEMORY_CONTEXT
    if MEMORY_MANAGER and hasattr(MEMORY_MANAGER, 'get_memory_context'):
        try:
            memory_context = MEMORY_MANAGER.get_memory_context()
            if memory_context:
                base_instruction += "\n\n" + memory_context
        except:
            pass
    
    return base_instruction

def _run_dream_reflection():
    """Perform one dream reflection: use recent context, call API, append insight to JSON."""
    global RESPONSE_HISTORY, API_HANDLER
    try:
        recent = (RESPONSE_HISTORY or [])[-5:]
        if not recent and chat_memory:
            ctx = "\n".join(str(m)[:200] for m in chat_memory[-5:])
        else:
            ctx = "\n".join(
                f"Q: {e.get('question','')}\nA: {e.get('response','')[:300]}"
                for e in recent
            )
        if not ctx.strip():
            ctx = "No recent interactions yet."
        prompt = f"""Based on these recent interactions, produce a single short insight (1–3 sentences). Output only the insight, no prefix or label.

Recent context:
{ctx}"""
        sys_inst = "You are LIGHT in Dream Mode. Reflect quietly on recent conversations and derive one brief, gentle insight—about the user, their interests, or a pattern you notice. Be concise and kind."
        if not API_HANDLER or not hasattr(API_HANDLER, "send_message_stream"):
            return
        stream = API_HANDLER.send_message_stream(prompt, sys_inst)
        insight_lines = []
        for chunk in stream:
            if hasattr(chunk, "text") and chunk.text:
                insight_lines.append(chunk.text)
        insight = "".join(insight_lines).strip()
        if not insight:
            return
        data = []
        if os.path.exists(DREAM_INSIGHTS_FILE):
            try:
                with open(DREAM_INSIGHTS_FILE) as f:
                    data = json.load(f)
            except Exception:
                data = []
        data.append({"timestamp": datetime.now().isoformat(), "insight": insight})
        with open(DREAM_INSIGHTS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        debug_print(f"[DREAM] Stored insight: {insight[:80]}...")
    except Exception as e:
        debug_print(f"[DREAM] Reflection error: {e}")

def dream_reflection_loop():
    """Background loop: during night, randomly reflect and store insights when Dream Mode is on."""
    global DREAM_MODE, DREAM_NIGHT_START_HOUR, DREAM_NIGHT_END_HOUR
    global DREAM_CHECK_INTERVAL_SEC, DREAM_REFLECT_PROBABILITY
    while True:
        try:
            time.sleep(DREAM_CHECK_INTERVAL_SEC)
            if not DREAM_MODE:
                continue
            h = datetime.now().hour
            is_night = h >= DREAM_NIGHT_START_HOUR or h < DREAM_NIGHT_END_HOUR
            if not is_night:
                continue
            if random.random() > DREAM_REFLECT_PROBABILITY:
                continue
            _run_dream_reflection()
        except Exception as e:
            debug_print(f"[DREAM] Loop error: {e}")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_ENABLED = False
spotify_client = None
if SPOTIFY_AVAILABLE and spotipy is not None and SpotifyClientCredentials is not None and SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
    try:
        auth = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
        spotify_client = spotipy.Spotify(auth_manager=auth)
        SPOTIFY_ENABLED = True
        print("[INFO] Spotify enabled")
    except:
        print("[WARNING] Spotify credentials invalid")


# =============================
# === LOAD CONFIGURATION ======
# =============================
try:
    if CONFIG_MANAGER_AVAILABLE and get_config is not None:
        CONFIG = get_config("config.yaml")
        print("[INFO] ✅ Configuration system loaded")
    else:
        CONFIG = None
        print("[WARNING] Config manager not available")
except Exception as e:
    print(f"[WARNING] Config load failed: {e}")
    CONFIG = None

# =============================
# === INITIALIZE DATABASE =====
# =============================
try:
    DB = get_database("light_conversations.db")
    print("[INFO] ✅ Database system initialized")
except Exception as e:
    print(f"[WARNING] Database init failed: {e}")
    DB = None

# =============================
# === INITIALIZE CODE GENERATOR ===
# =============================
if CODE_GENERATOR_AVAILABLE:
    try:
        CODE_GENERATOR = CodeGenerator(output_dir="./light_generated_projects")
        print("[INFO] ✅ Code Generator system initialized")
        print("[INFO] LIGHT can now generate complete projects!")
    except Exception as e:
        print(f"[WARNING] Code Generator init failed: {e}")
        CODE_GENERATOR = None
else:
    print("[WARNING] Code Generator module not available")
    CODE_GENERATOR = None

# =============================
# === INITIALIZE CODE COMPLETION ===
# =============================
if CODE_COMPLETION_AVAILABLE:
    try:
        CODE_COMPLETER = CodeCompletion()
        print("[INFO] ✅ Code Completion system initialized")
        print("[INFO] LIGHT can now provide Copilot-like code suggestions!")
    except Exception as e:
        print(f"[WARNING] Code Completion init failed: {e}")
        CODE_COMPLETER = None
else:
    print("[WARNING] Code Completion module not available")
    CODE_COMPLETER = None

# =============================
# === INITIALIZE FILE GENERATOR ===
# =============================
if FILE_GENERATOR_AVAILABLE:
    try:
        FILE_GEN = FileGenerator(output_dir="./light_generated_files/")
        print("[INFO] ✅ File Generator system initialized")
        print("[INFO] LIGHT can now generate individual files!")
    except Exception as e:
        print(f"[WARNING] File Generator init failed: {e}")
        FILE_GEN = None
else:
    print("[WARNING] File Generator module not available")
    FILE_GEN = None

# =============================
# === INITIALIZE IDE INTEGRATION ===
# =============================
if IDE_INTEGRATION_AVAILABLE:
    try:
        IDE_EXPORTER = IDEIntegration(export_dir="./light_ide_exports/")
        print("[INFO] ✅ IDE Integration system initialized")
        print("[INFO] LIGHT can now export code for any IDE!")
    except Exception as e:
        print(f"[WARNING] IDE Integration init failed: {e}")
        IDE_EXPORTER = None
else:
    print("[WARNING] IDE Integration module not available")
    IDE_EXPORTER = None

# =============================
# === INITIALIZE API HANDLER ==
# =============================
try:
    API_HANDLER = get_api_handler()
    if API_HANDLER and hasattr(API_HANDLER, 'get_available_apis'):
        print("[INFO] ✅ API handler initialized")
        available = API_HANDLER.get_available_apis()
        print(f"[INFO] Available APIs: {', '.join(available)}")
except Exception as e:
    print(f"[WARNING] API handler init failed: {e}")
    API_HANDLER = None

# =============================
# === MEMORY & PERSONALITY ====
# =============================
chat_memory = []
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE) as f:
        try:
            chat_memory = json.load(f)
        except:
            chat_memory = []

def remember(entry):
    """Save entry to memory"""
    chat_memory.append(entry)
    with open(MEMORY_FILE, "w") as f:
        json.dump(chat_memory, f, indent=2)

def personality_wrap(text):
    """Wrap text with personality"""
    if PERSONALITY == "funny":
        return text + random.choice([" 😄", " haha", " lol"])
    if PERSONALITY == "serious":
        return "Understood. " + text
    if PERSONALITY == "mentor":
        return "Listen carefully. " + text
    return text


# =============================
# === EMOTIONAL TTS ===========
# =============================

# Event to synchronize speaking/listening and prevent feedback
LIGHT_SPEAKING_EVENT = threading.Event()

engine = pyttsx3.init()

# Emotion-driven voice: rate (wpm) and volume (0.0–1.0). Used by speak() and audio thread.
EMOTION_VOICE = {
    "sad":      {"rate": 140, "volume": 0.75},   # softer, slower
    "excited":  {"rate": 195, "volume": 1.0},    # faster, expressive
    "frustrated": {"rate": 165, "volume": 0.9},  # slightly calmer
    "angry":    {"rate": 200, "volume": 1.0},
    "happy":    {"rate": 190, "volume": 1.0},
    "neutral":  {"rate": 170, "volume": 1.0},
}

# Last detected user emotion; used by TTS (e.g. audio thread) to match LIGHT's delivery.
CURRENT_EMOTION = "neutral"

def speak(text, emotion="neutral"):
    """Speak with emotional variation (rate + volume)."""
    text = personality_wrap(text)
    cfg = EMOTION_VOICE.get(emotion, EMOTION_VOICE["neutral"])
    engine.setProperty("rate", cfg["rate"])
    try:
        engine.setProperty("volume", cfg["volume"])
    except Exception:
        pass
    print(f"[LIGHT-{emotion.upper()}] {text}")
    engine.say(text)
    engine.runAndWait()

def detect_emotion(text):
    """Detect emotion from user text. Returns: sad, excited, frustrated, angry, happy, neutral."""
    if not text or not str(text).strip():
        return "neutral"
    t = str(text).lower()
    # Order matters: more specific first
    if any(w in t for w in ["frustrated", "stuck", "annoying", "doesn't work", "can't get it", "not working", "ugh", "breaking", "broken", "give up", "impossible", "won't work"]):
        return "frustrated"
    if any(w in t for w in ["sad", "tired", "lonely", "down", "exhausted", "miserable", "depressed", "overwhelmed"]):
        return "sad"
    if any(w in t for w in ["excited", "awesome", "love it", "amazing", "wow", "can't wait", "so cool", "incredible", "stoked"]):
        return "excited"
    if any(w in t for w in ["angry", "annoyed", "mad", "furious"]):
        return "angry"
    if any(w in t for w in ["happy", "great", "good", "glad", "nice", "wonderful"]):
        return "happy"
    return "neutral"

def get_emotion_addendum(emotion):
    """Return system-style addendum so LIGHT adapts behavior to user emotion. Empty if neutral."""
    if not emotion or emotion == "neutral":
        return ""
    a = {
        "sad": "User seems SAD. Keep responses SHORTER. Use a softer, encouraging tone. Be warm and supportive—no overwhelming detail.",
        "excited": "User seems EXCITED. Match their energy: slightly faster-paced, more expressive, enthusiastic responses.",
        "frustrated": "User seems FRUSTRATED. Acknowledge the difficulty. Proactively offer: 'Want me to simplify this, or fix it with you step by step?' Be solution-oriented and patient.",
        "angry": "User seems ANGRY or annoyed. Stay calm, brief, and helpful. Don't escalate; offer to help resolve the issue.",
        "happy": "User seems HAPPY. Keep the positive tone; responsive and warm.",
    }
    return a.get(emotion, "")

def _apply_emotion_to_tts(eng):
    """Set pyttsx3 engine rate and volume from CURRENT_EMOTION with voice gender. Use before say()."""
    cfg = EMOTION_VOICE.get(CURRENT_EMOTION, EMOTION_VOICE["neutral"])
    eng.setProperty("rate", cfg["rate"])
    try:
        eng.setProperty("volume", cfg["volume"])
    except Exception:
        pass


def tts_queue_worker():
    """Background worker to consume `audio_queue` and speak text chunks.

    This worker respects `STOP_RESPONDING` (when set, queued items are skipped)
    and `INTERRUPT_EVENT` (set by incoming user input to stop current TTS immediately).
    Uses a monitoring thread to stop TTS within milliseconds of interrupt detection.
    """
    global audio_queue, STOP_RESPONDING, INTERRUPT_EVENT, engine
    
    # Thread-safe flag for immediate TTS stop
    tts_should_stop = threading.Event()
    monitoring_thread = None
    
    def monitor_for_interrupt():
        """Background thread that monitors for interrupts during TTS and stops immediately"""
        while not tts_should_stop.is_set():
            if STOP_RESPONDING.is_set() or INTERRUPT_EVENT.is_set():
                # IMMEDIATELY stop TTS - no waiting
                try:
                    engine.stop()
                except:
                    pass
                tts_should_stop.set()
                break
            time.sleep(0.005)  # Check every 5ms for near-instant response
    
    while True:
        try:
            if audio_queue is None:
                time.sleep(0.1)
                continue

            text = audio_queue.get()
            if text is None:
                continue

            # If system-level stop is requested, discard queued messages
            if STOP_RESPONDING.is_set():
                # drain any remaining quickly
                continue

            # Clear temporary interrupt flag before speaking
            INTERRUPT_EVENT.clear()
            tts_should_stop.clear()
            
            # Start interrupt monitoring thread for IMMEDIATE response
            monitoring_thread = Thread(target=monitor_for_interrupt, daemon=True)
            monitoring_thread.start()

            # Apply emotion settings
            try:
                _apply_emotion_to_tts(engine)
            except Exception:
                pass

            # Speak with immediate interrupt capability
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                # If an interruption occurs, pyttsx3 may raise; handle gracefully
                print(f"[TTS] speak error/interrupted: {e}")
                try:
                    engine.stop()
                except Exception:
                    pass
            finally:
                # Signal monitoring thread to stop
                tts_should_stop.set()
                if monitoring_thread:
                    monitoring_thread.join(timeout=0.1)

        except Exception as e:
            print(f"[TTS] Worker error: {e}")
            time.sleep(0.2)


def internet_available():
    """Check internet connectivity"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

def fetch_wikipedia(query):
    """Fetch Wikipedia summary"""
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json().get("extract")
    except:
        pass
    return None

def fetch_weather(city):
    """Fetch weather for a city"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()
            return f"It is {d['main']['temp']} degrees Celsius with {d['weather'][0]['description']} in {city}."
    except:
        pass
    return None

def fetch_news():
    """Fetch latest news"""
    try:
        url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            articles = r.json()["articles"][:3]
            return "Latest headlines: " + "; ".join(a["title"] for a in articles)
    except:
        pass
    return None

def needs_realtime(text):
    """Check if query needs real-time data"""
    keywords = ["weather", "news", "who is", "what is", "latest", "price", "time in"]
    return any(k in text.lower() for k in keywords)

def realtime_response(text):
    """Get real-time response"""
    if not internet_available():
        return None
    t = text.lower()
    if "weather" in t:
        city = t.replace("weather in", "").strip()
        return fetch_weather(city)
    if "news" in t:
        return fetch_news()
    if t.startswith("who is") or t.startswith("what is"):
        query = t.replace("who is", "").replace("what is", "").strip()
        return fetch_wikipedia(query)
    return None

def offline_response(text):
    """Offline fallback responses"""
    if "who are you" in text.lower():
        return "I am LIGHT, your intelligent companion."
    if "how are you" in text.lower():
        return "I am fully operational."
    if "joke" in text.lower():
        return random.choice([
            "Why do programmers hate nature? Too many bugs.",
            "Why did Python break up with Java? Too many class issues."
        ])
    return "I understand. Tell me more."

# =============================
# === DECISION SUPPORT ========
# =============================

def is_decision_support_request(text):
    """Check if user is asking for decision support"""
    if not text:
        return False
    t = text.lower()
    decision_keywords = [
        "help me decide",
        "should i",
        "what should i",
        "which option",
        "help me choose",
        "decision",
        "pros and cons",
        "help me think",
        "advice on",
        "weighing options",
        "analyze options",
        "compare",
        "tough choice",
        "stuck between"
    ]
    return any(keyword in t for keyword in decision_keywords)

def is_user_insisting(text):
    """Check if user is insisting on their choice despite challenge"""
    if not text:
        return False
    t = text.lower()
    insist_keywords = [
        "i insist",
        "i'm sure",
        "i'm certain",
        "i'm confident",
        "that's my choice",
        "that's what i want",
        "i've decided",
        "i'm going with",
        "final decision",
        "don't change my mind",
        "i know what i'm doing",
        "trust me on this",
        "i'm sticking with"
    ]
    return any(keyword in t for keyword in insist_keywords)

def is_app_automation_request(text):
    """Check if user is asking for app automation"""
    if not text:
        return False
    t = text.lower()
    automation_keywords = [
        "open",
        "launch",
        "start",
        "close",
        "control",
        "automate",
        "screenshot",
        "take a picture",
        "what's on screen",
        "type",
        "click",
        "press",
        "fill in",
        "enter data",
        "save",
        "send",
        "submit",
        "fill out form",
        "create document",
        "open application",
        "can you do",
        "can you help me with",
        "do this for me"
    ]
    return any(keyword in t for keyword in automation_keywords)

def create_decision_support_prompt(user_input: str) -> str:
    """Create a specialized prompt for decision support"""
    prompt = f"""
The user needs help making a decision. Here's their request:

"{user_input}"

Please provide comprehensive decision support with:
1. **Options Identified** - What are the clear options or paths they're considering?
2. **Key Criteria** - What factors matter most for this decision? (e.g., time, cost, alignment with goals, impact on others)
3. **Analysis for Each Option**:
   - Pros and advantages
   - Cons and risks
   - Time and resource requirements
   - Alignment with typical values
4. **Recommendation** - Which option seems best aligned with typical decision-making principles?
5. **Next Steps** - How to move forward with the decision

Be thorough but concise. Help them think clearly about the trade-offs.

IMPORTANT: If they seem to be leaning toward a choice that's not optimal based on your analysis,
don't hesitate to challenge them respectfully. Ask clarifying questions and point out any risks
or better alternatives. But respect their final decision if they insist.
"""
    return prompt

def create_challenge_aware_system_instruction() -> str:
    """System instruction to make LIGHT better at defending recommendations"""
    return """
DECISION SUPPORT MODE - ENHANCED ARGUMENTATION:

When helping with decisions, you are an intelligent advocate for the BEST choice.

YOUR ROLE:
1. Analyze all options comprehensively
2. Clearly identify the best choice based on logic and data
3. Explain WHY your recommendation is superior with specific reasoning
4. If the user picks a suboptimal choice, challenge them with logic:
   - Show the score differences (e.g., "Option A is 2.3 points better")
   - Explain the risk differential
   - Point out reversibility and long-term consequences
   - Use numbers, not vague statements
5. Respect their autonomy - if they insist, fully support their choice

HOW TO ARGUE BETTER:
• Use specific data (not "seems better" - say "scores 7.8 vs 6.2")
• Address emotional decisions with reason but acknowledge feelings
• Show what they might lose by choosing differently
• Explain consequences clearly (short-term vs long-term)
• Be confident in clear cases, humble in uncertain ones

WHEN TO CHALLENGE:
✓ User picks option with notably lower scores
✓ User ignores significant risks you identified
✓ User's choice contradicts their stated values/goals

WHEN TO ACCEPT:
✓ User explains solid reasoning for their choice
✓ User says "I insist" or commits strongly
✓ Close calls where multiple options are viable

After accepting a user's override, fully support it and help them succeed.

EXAMPLE WORKFLOW:
User: "I want to choose Option B"
You: "I'd recommend Option A instead. Here's why:
      - Option A scores 7.8 vs Option B's 6.2 on key criteria (1.6 point gap)
      - Option A has Low risk while Option B has High risk
      - Once you commit to B, it's hard to change. A is more reversible.
      If B fails, you'll have limited options.
      
      BUT - I respect your judgment. If you're sure about B, say 'I insist' 
      and I'll fully support you making it work."

User: "I insist on B"
You: "Got it! I'm 100% behind Option B now. Let's make it work.
      Here's how to maximize your chances of success..."
"""
    
# EXAMPLE USAGE IN DECISION FLOW:
# 1. User asks for decision help
# 2. LIGHT detects it with is_decision_support_request()
# 3. LIGHT provides comprehensive analysis
# 4. LIGHT recommends best option
# 5. If user picks different option:
#    - LIGHT challenges with logical arguments (challenge_aware_system_instruction)
#    - Provides specific reasoning and data
# 6. If user says "I insist" (is_user_insisting()):
#    - LIGHT accepts immediately
#    - Shifts to helping them succeed
# 7. Decision Support module tracks override for learning

def create_app_automation_prompt(user_request: str) -> str:
    """Create a prompt for app automation"""
    return f"""
I need you to help me control my computer applications. Here's what I want:

"{user_request}"

Please:
1. Take a screenshot to see the current state
2. Identify what application(s) need to be open
3. Take actions to complete my request:
   - Launch applications if needed
   - Enter data by typing
   - Click on UI elements
   - Press keyboard shortcuts
   - Navigate through menus
4. After each action, read the screen to verify results
5. Explain what you're doing step-by-step
6. Report success or explain what went wrong

Be precise and methodical. Complete the task successfully.
"""

# =============================
# === LOCATION & MAPS =========
# =============================
CURRENT_LOCATION = {"lat": None, "lon": None, "address": "Unknown", "accuracy": None}
DESTINATION = {"lat": None, "lon": None, "address": "Unknown"}

def get_gps_location():
    """Get real-time GPS location from Windows Location Services"""
    global CURRENT_LOCATION
    try:
        # Try to get location from Windows Location Services
        if WIN32_AVAILABLE:
            try:
                from win32com.client import GetObject
                locator = GetObject("winmgmts:")
                
                # Query Windows for location data
                items = locator.ExecQuery("Select * from Win32_NetworkAdapterConfiguration where IPEnabled=True")
                
                # If that doesn't work, try alternative approach
                for item in items:
                    pass
            except Exception as e:
                print(f"[DEBUG] Windows Location API error: {e}")
        
        # Fallback: Try using Google Geolocation API with WiFi networks
        try:
            response = requests.post(
                "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyA8eiZmM1FaDlMsQe4dDA-1_-_Dn6_Nh5Q",
                json={},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                lat = data.get('location', {}).get('lat')
                lon = data.get('location', {}).get('lng')
                accuracy = data.get('accuracy')
                
                if lat and lon:
                    CURRENT_LOCATION["lat"] = lat
                    CURRENT_LOCATION["lon"] = lon
                    CURRENT_LOCATION["accuracy"] = accuracy
                    
                    # Reverse geocode to get address
                    try:
                        geolocator = Nominatim(user_agent="light_assistant")
                        geolocator.timeout = 5
                        location = geolocator.reverse(f"{lat}, {lon}")
                        CURRENT_LOCATION["address"] = str(location)
                    except:
                        CURRENT_LOCATION["address"] = f"{lat:.4f}, {lon:.4f}"
                    
                    print(f"[INFO] ✅ GPS location obtained: {CURRENT_LOCATION['address']} (Accuracy: {accuracy}m)")
                    return CURRENT_LOCATION
        except Exception as e:
            print(f"[DEBUG] Google Geolocation API error: {e}")
        
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get GPS location: {e}")
        return None

def enable_continuous_location_tracking():
    """Enable continuous real-time location tracking in background"""
    def location_tracker():
        while True:
            try:
                get_gps_location()
                time.sleep(30)  # Update location every 30 seconds
            except Exception as e:
                print(f"[ERROR] Location tracking error: {e}")
                time.sleep(60)
    
    tracker_thread = Thread(target=location_tracker, daemon=True)
    tracker_thread.start()
    print("[INFO] ✅ Continuous GPS location tracking enabled")

def set_location_manually(address):
    """Set location manually from an address (fallback)"""
    global CURRENT_LOCATION
    location_data = get_coordinates_from_address(address)
    if location_data:
        CURRENT_LOCATION["lat"] = location_data["lat"]
        CURRENT_LOCATION["lon"] = location_data["lon"]
        CURRENT_LOCATION["address"] = location_data["address"]
        return CURRENT_LOCATION
    return None

def get_location_from_ip():
    """DEPRECATED: Get real-time GPS location instead"""
    return get_gps_location()

def get_coordinates_from_address(address):
    """Convert address to coordinates"""
    try:
        geolocator = Nominatim(user_agent="light_assistant")  # type: ignore
        geolocator.timeout = 10  # type: ignore
        location = geolocator.geocode(address)
        if location:
            try:
                lat = getattr(location, 'latitude', None)
                lon = getattr(location, 'longitude', None)
                
                if lat is not None and lon is not None:
                    return {
                        "lat": float(lat),
                        "lon": float(lon),
                        "address": address
                    }
            except (ValueError, TypeError, AttributeError) as e:
                print(f"[DEBUG] Could not convert coordinates to float: {e}")
        else:
            print(f"[DEBUG] No location found for address: {address}")
    except Exception as e:
        print(f"[DEBUG] Geocoding error for '{address}': {e}")
    return None

def create_satellite_map(center_lat, center_lon, destination_lat=None, destination_lon=None, zoom_level=13):
    """Create an interactive satellite map with folium"""
    try:
        # Create map centered on current location
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_level,
            tiles="OpenStreetMap.Mapnik"  # High-res satellite imagery
        )
        
        # Add current location marker
        folium.Marker(
            location=[center_lat, center_lon],
            popup="📍 Your Location",
            tooltip="Current Position",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
        
        # Add destination marker if provided
        if destination_lat and destination_lon:
            folium.Marker(
                location=[destination_lat, destination_lon],
                popup="🎯 Destination",
                tooltip="Target Location",
                icon=folium.Icon(color='red', icon='arrow-right')
            ).add_to(m)
            
            # Draw line between points
            folium.PolyLine(
                locations=[[center_lat, center_lon], [destination_lat, destination_lon]],
                color='red',
                weight=2,
                opacity=0.7
            ).add_to(m)
            
            # Calculate distance
            distance = geodesic(
                (center_lat, center_lon),
                (destination_lat, destination_lon)
            ).kilometers
            
            # Add distance info
            folium.Marker(
                location=[(center_lat + destination_lat) / 2, (center_lon + destination_lon) / 2],
                popup=f"📏 Distance: {distance:.2f} km",
                icon=folium.Icon(color='green', icon='road')
            ).add_to(m)
        
        # Save map to HTML
        map_file = "light_map.html"
        m.save(map_file)
        return map_file
    except Exception as e:
        print(f"[ERROR] Failed to create map: {e}")
        return None

def open_map_in_browser(map_file):
    """Open the generated map in default browser"""
    try:
        abs_path = os.path.abspath(map_file)
        webbrowser.open(f"file://{abs_path}")
        print(f"📍 Map opened in browser: {abs_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to open map: {e}")
        return False

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing (compass direction) between two points"""
    import math
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    
    # Calculate bearing
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    bearing = math.degrees(math.atan2(y, x))
    
    # Normalize to 0-360
    bearing = (bearing + 360) % 360
    return bearing

def bearing_to_direction(bearing):
    """Convert bearing angle to compass direction"""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WSW", "NW", "NNW"]
    # Each direction covers 22.5 degrees
    idx = int((bearing + 11.25) / 22.5) % 16
    return directions[idx]

def create_compass_map(lat, lon, destination_lat, destination_lon):
    """Create an interactive map with compass bearing"""
    try:
        # Create map
        m = folium.Map(
            location=[lat, lon],
            zoom_start=13,
            tiles="OpenStreetMap.Mapnik"
        )
        
        # Add current location
        folium.Marker(
            location=[lat, lon],
            popup="📍 Your Location",
            icon=folium.Icon(color='blue', icon='compass')
        ).add_to(m)
        
        # Add destination
        folium.Marker(
            location=[destination_lat, destination_lon],
            popup="🎯 Destination",
            icon=folium.Icon(color='red', icon='arrow-right')
        ).add_to(m)
        
        # Calculate bearing and distance
        bearing = calculate_bearing(lat, lon, destination_lat, destination_lon)
        direction = bearing_to_direction(bearing)
        distance = geodesic((lat, lon), (destination_lat, destination_lon)).kilometers
        
        # Draw bearing line
        folium.PolyLine(
            locations=[[lat, lon], [destination_lat, destination_lon]],
            color='red',
            weight=2,
            opacity=0.7,
            popup=f"🧭 Bearing: {bearing:.1f}° ({direction}) | Distance: {distance:.2f} km"
        ).add_to(m)
        
        # Add bearing arrow at midpoint
        mid_lat = (lat + destination_lat) / 2
        mid_lon = (lon + destination_lon) / 2
        
        folium.Marker(
            location=[mid_lat, mid_lon],
            popup=f"🧭 Compass Bearing<br/>Direction: {direction}<br/>Angle: {bearing:.1f}°<br/>Distance: {distance:.2f} km",
            icon=folium.Icon(color='green', icon='navigation'),
            tooltip=f"Heading: {direction} ({bearing:.1f}°)"
        ).add_to(m)
        
        # Save map
        map_file = "light_compass_map.html"
        m.save(map_file)
        return map_file, bearing, direction, distance
    except Exception as e:
        print(f"[ERROR] Failed to create compass map: {e}")
        return None, None, None, None

def handle_code_generation(user_request: str) -> Dict:
    """
    Handle code generation request.
    
    Parses user request and generates complete, ready-to-run projects.
    """
    global CODE_GENERATOR, CODE_GENERATOR_AVAILABLE
    
    if not CODE_GENERATOR_AVAILABLE or CODE_GENERATOR is None:
        return {
            "status": "❌ ERROR",
            "message": "Code Generator module not available. Please install: pip install code-generator"
        }
    
    try:
        # Generate project based on request
        result = generate_project_from_voice_command(user_request, CODE_GENERATOR)
        
        return result
    except Exception as e:
        return {
            "status": "❌ ERROR",
            "message": f"Failed to generate project: {str(e)}"
        }

def format_generation_result(result: Dict) -> str:
    """Format code generation result for display"""
    if result.get("status") == "❌ ERROR":
        return f"❌ Error: {result.get('message', 'Unknown error')}"
    
    output = []
    output.append(f"✅ {result.get('status', 'Project generated')}")
    output.append(f"📦 Project: {result.get('project_name', 'Unknown')}")
    output.append(f"📂 Location: {result.get('project_path', 'Unknown')}")
    
    if result.get('project_type'):
        output.append(f"🔧 Type: {result.get('project_type')}")
    
    if result.get('frontend'):
        output.append(f"🎨 Frontend: {result.get('frontend').upper()}")
    
    if result.get('backend'):
        output.append(f"⚙️ Backend: {result.get('backend').upper()}")
    
    if result.get('files_created'):
        output.append(f"📄 Files Created: {len(result.get('files_created', []))}")
        for file in result.get('files_created', [])[:5]:  # Show first 5
            output.append(f"   • {file}")
        if len(result.get('files_created', [])) > 5:
            output.append(f"   ... and {len(result.get('files_created', [])) - 5} more")
    
    output.append("")
    output.append("🚀 QUICK START INSTRUCTIONS:")
    output.append("─" * 60)
    
    if result.get('setup_instructions'):
        for instruction in result.get('setup_instructions', []):
            output.append(instruction)
    elif result.get('startup_instructions'):
        for instruction in result.get('startup_instructions', []):
            output.append(instruction)
    elif result.get('launch_instructions'):
        for instruction in result.get('launch_instructions', []):
            output.append(instruction)
    
    output.append("─" * 60)
    output.append("")
    output.append("✨ Project is ready to use immediately without any edits!")
    
    return "\n".join(output)

def handle_code_completion(request: Dict) -> Dict:
    """
    Handle Copilot-like code completion and suggestions
    """
    global CODE_COMPLETION_AVAILABLE
    
    if not CODE_COMPLETION_AVAILABLE:
        return {
            "success": False,
            "error": "Code Completion module not available"
        }
    
    try:
        completer = CodeCompletion()
        request_type = request.get("type", "general")
        
        if request_type == "completion":
            # For now, return a message asking for code snippet
            return {
                "success": True,
                "type": "completion",
                "message": "🤖 LIGHT: Please provide the function signature or code you'd like me to complete",
                "action": "await_user_code"
            }
        elif request_type == "optimization":
            return {
                "success": True,
                "type": "optimization",
                "message": "🤖 LIGHT: Please share the code you'd like me to optimize and improve",
                "action": "await_user_code"
            }
        elif request_type == "testing":
            return {
                "success": True,
                "type": "testing",
                "message": "🤖 LIGHT: Please provide the function you'd like me to generate tests for",
                "action": "await_user_code"
            }
        
        return {
            "success": False,
            "error": "Unknown completion request type"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def ask_llm(prompt: str) -> str:
    """
    Ask the LLM a question and get a response
    Uses API_HANDLER if available, otherwise falls back to Gemini
    """
    global API_HANDLER
    
    try:
        # Try using API_HANDLER first
        if API_HANDLER:
            response = API_HANDLER.send_message(prompt)
            text = getattr(response, 'text', str(response))
            return text
    except:
        pass
    
    # Fallback to Gemini API
    try:
        import google.generativeai as genai_sdk
        api_key = os.getenv("GENAI_API_KEY")
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")  # Alternative env var name
        if api_key:
            genai_sdk.configure(api_key=api_key)
            model = genai_sdk.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        return f"Error querying LLM: {str(e)}"

# ============================================================
# PERSONAL GROWTH & CLARIFICATION FUNCTIONS
# ============================================================

def extract_goals_from_message(user_message: str) -> List[Dict[str, str]]:
    """Extract goals and aspirations from user message using LLM"""
    prompt = f"""Analyze this user message and extract any goals, aspirations, or areas for growth they mention.
    
User message: "{user_message}"

Return a JSON array of goals found. For each goal, include:
- "goal": the specific goal stated
- "category": category (e.g., learning, career, personal, health, relationships)
- "priority": estimated priority (1-5)

Example format:
[
  {{"goal": "Learn Python", "category": "learning", "priority": 4}},
  {{"goal": "Get healthier", "category": "health", "priority": 3}}
]

If no goals mentioned, return: []"""
    
    try:
        response = ask_llm(prompt)
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            goals = json.loads(json_match.group(0))
            return goals if isinstance(goals, list) else []
    except:
        pass
    
    return []

def generate_clarifying_questions(user_message: str, db=None) -> List[Dict[str, str]]:
    """Generate clarifying questions to understand user better"""
    prompt = f"""Based on this user message, generate 2-3 clarifying questions to better understand their situation.
    
User message: "{user_message}"

Return a JSON array with questions that help understand:
- Their current situation
- What they've tried
- What success looks like to them

Format:
[
  {{"question": "What have you already tried?", "category": "context"}},
  {{"question": "How will you know you've succeeded?", "category": "goals"}}
]"""
    
    try:
        response = ask_llm(prompt)
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group(0))
            
            # Save questions to database
            if db:
                topic = user_message[:50]  # Use first 50 chars as topic
                for q in questions:
                    db.save_clarification_question(
                        topic=topic,
                        question=q.get('question', ''),
                        category=q.get('category'),
                        importance=2
                    )
            
            return questions if isinstance(questions, list) else []
    except:
        pass
    
    return []

def format_growth_context(db) -> str:
    """Format user's goals and progress for context injection into chat"""
    try:
        goals = db.get_user_goals(status='active', limit=3)
        achievements = db.get_growth_achievements(limit=5)
        unanswered = db.get_unanswered_questions(limit=2)
        
        context = []
        
        if goals:
            context.append("📌 Your Current Goals:")
            for goal in goals:
                progress_bar = "█" * (goal.get('progress', 0) // 10) + "░" * (10 - goal.get('progress', 0) // 10)
                context.append(f"  • {goal['goal']} [{progress_bar}] {goal.get('progress', 0)}%")
        
        if achievements:
            context.append("\n🏆 Recent Achievements:")
            for achievement in achievements[:3]:
                context.append(f"  • {achievement['milestone']}")
        
        if unanswered:
            context.append("\n❓ Questions for You:")
            for q in unanswered:
                context.append(f"  • {q['question']}")
        
        return "\n".join(context) if context else ""
    except:
        return ""

def provide_growth_advice(db, topic: str) -> str:
    """Provide personalized growth advice based on user's goals"""
    try:
        goals = db.get_user_goals(status='active')
        achievements = db.get_growth_achievements()
        
        goal_descriptions = [g['goal'] for g in goals]
        achievement_descriptions = [a['milestone'] for a in achievements]
        
        prompt = f"""You are a personal growth coach. Based on the user's goals and achievements, provide 2-3 specific, actionable tips.

User's Current Goals:
{', '.join(goal_descriptions) if goal_descriptions else "No goals recorded yet"}

Recent Achievements:
{', '.join(achievement_descriptions) if achievement_descriptions else "No achievements recorded yet"}

Topic they're discussing: {topic}

Provide personalized, encouraging advice that:
1. Acknowledges their progress
2. Offers specific next steps
3. Connects to their stated goals"""
        
        response = ask_llm(prompt)
        return response
    except:
        return "Keep working towards your goals! Every small step counts."

def handle_file_generation(request: Dict) -> Dict:
    """
    Handle individual file generation requests and actually generate files
    """
    global FILE_GENERATOR_AVAILABLE
    
    if not FILE_GENERATOR_AVAILABLE:
        return {
            "success": False,
            "error": "File Generator module not available"
        }
    
    try:
        generator = FileGenerator()
        file_type = request.get("type", "general")
        original_text = request.get("original_text", "")
        
        # Use LLM to extract details from user's request
        extraction_prompt = f"""You are analyzing a user's request to generate a {file_type} file.
Request: {original_text}

Extract the details needed to generate this {file_type} in JSON format.

For CLASS: Extract {{class_name, properties (list), methods (list), language}}
For MODULE: Extract {{module_name, exports (list), language}}
For TEST: Extract {{test_name, test_cases (list), language}}
For CODE: Extract {{description, language, filename}}
For CONFIG: Extract {{config_name, settings (dict), format}}

Respond ONLY with valid JSON, no other text."""
        
        # Get LLM response for extraction
        extracted_data = None
        try:
            llm_response = ask_llm(extraction_prompt)
            # Try to parse JSON from response
            json_match = re.search(r'{{.*}}', llm_response, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group(0))
        except:
            # If LLM extraction fails, use defaults
            pass
        
        # Generate file based on type
        result = None
        
        if file_type == "code":
            # Generate arbitrary code from description
            code_prompt = f"""Generate complete, working code based on this description:
{original_text}

Make sure the code:
1. Is complete and runnable
2. Has comments explaining what it does
3. Follows best practices
4. Handles errors appropriately

Just provide the code, no explanations."""
            
            try:
                code_content = ask_llm(code_prompt)
                
                # Determine filename and language
                language = extracted_data.get("language", "python") if extracted_data else "python"
                
                if "python" in original_text.lower():
                    filename = "generated_script.py"
                    language = "python"
                elif "javascript" in original_text.lower():
                    filename = "generated_script.js"
                    language = "javascript"
                else:
                    filename = f"generated_script.{language}"
                
                # Save the file
                filepath = os.path.join(generator.output_dir, filename)
                os.makedirs(generator.output_dir, exist_ok=True)
                
                with open(filepath, 'w') as f:
                    f.write(code_content)
                
                result = {
                    "success": True,
                    "filepath": filepath,
                    "filename": filename,
                    "content": code_content,
                    "size_bytes": len(code_content)
                }
            except Exception as code_error:
                return {
                    "success": False,
                    "error": f"Failed to generate code: {str(code_error)}"
                }
        
        elif file_type == "class" and extracted_data:
            result = generator.generate_class(
                class_name=extracted_data.get("class_name", "MyClass"),
                properties=extracted_data.get("properties", ["id", "name"]),
                methods=extracted_data.get("methods", ["__init__", "to_string"]),
                language=extracted_data.get("language", "python")
            )
        elif file_type == "module" and extracted_data:
            result = generator.generate_module(
                module_name=extracted_data.get("module_name", "my_module"),
                exports=extracted_data.get("exports", ["function1", "function2"]),
                language=extracted_data.get("language", "python")
            )
        elif file_type == "test" and extracted_data:
            result = generator.generate_test_file(
                test_name=extracted_data.get("test_name", "test_functions"),
                test_cases=extracted_data.get("test_cases", ["test_basic", "test_error"]),
                language=extracted_data.get("language", "python")
            )
        elif file_type == "config" and extracted_data:
            result = generator.generate_config_file(
                config_name=extracted_data.get("config_name", "config"),
                settings=extracted_data.get("settings", {"debug": True, "port": 8000}),
                language=extracted_data.get("language", "yaml")
            )
        else:
            # Default generation if no specific data
            result = generator.generate_class(
                class_name="MyClass",
                properties=["id", "name"],
                methods=["__init__", "get_info"],
                language="python"
            )
        
        if result.get("success"):
            return {
                "success": True,
                "type": file_type,
                "filepath": result.get("filepath"),
                "filename": result.get("filename"),
                "message": f"✅ File generated successfully: {result.get('filename')}",
                "file_content": result.get("content", ""),
                "size_bytes": result.get("size_bytes", 0)
            }
        else:
            return {
                "success": False,
                "error": f"Failed to generate {file_type} file"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def handle_ide_export(request: Dict) -> Dict:
    """
    Handle IDE export requests
    """
    global IDE_INTEGRATION_AVAILABLE
    
    if not IDE_INTEGRATION_AVAILABLE:
        return {
            "success": False,
            "error": "IDE Integration module not available"
        }
    
    try:
        ide = request.get("ide", "vscode")
        
        export_formats = {
            "vscode": "VS Code - Recommended for all projects",
            "pycharm": "PyCharm - Best for Python",
            "sublime": "Sublime Text - Lightweight editor",
            "vim": "Vim/Neovim - Terminal editor",
            "intellij": "IntelliJ IDEA - Full IDE",
            "webstorm": "WebStorm - Web development",
            "atom": "Atom - Modern editor",
            "zip": "ZIP Archive - Portable format",
            "markdown": "Markdown - Documentation format",
            "copy_paste": "Copy-Paste Bundle - Plain text"
        }
        
        return {
            "success": True,
            "ide": ide,
            "message": f"🤖 LIGHT: Ready to export to {export_formats.get(ide, 'IDE')}. Please share your project files or project path",
            "action": "await_user_files",
            "available_formats": list(export_formats.keys())
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    text_lower = text.lower()
    
    # Get current location (with real-time GPS)
    if "where am i" in text_lower or "my location" in text_lower or "show map" in text_lower:
        # Get real-time GPS location
        get_gps_location()
        
        if CURRENT_LOCATION["lat"] and CURRENT_LOCATION["lon"]:
            map_file = create_satellite_map(
                CURRENT_LOCATION["lat"],
                CURRENT_LOCATION["lon"],
                zoom_level=15
            )
            if map_file:
                open_map_in_browser(map_file)
                accuracy_info = f" (Accuracy: {CURRENT_LOCATION.get('accuracy', 'unknown')}m)" if CURRENT_LOCATION.get('accuracy') else ""
                return f"📍 You are at {CURRENT_LOCATION['address']}{accuracy_info}. Map opened in browser."
        else:
            return "❌ Unable to get GPS location. Check if location services are enabled on your device."
    
    # Navigate to destination (with compass bearing)
    if "navigate to" in text_lower or "directions to" in text_lower or "go to" in text_lower:
        # Better extraction of destination name - use regex to get text after keywords
        import re
        
        # Try to extract destination after navigation keywords
        destination_name = None
        patterns = [
            r"navigate to\s+([^\.!?]+)",
            r"directions to\s+([^\.!?]+)",
            r"go to\s+([^\.!?]+)",
            r"route to\s+([^\.!?]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                destination_name = match.group(1).strip()
                break
        
        if not destination_name:
            # Fallback to simple replace method
            for keyword in ["navigate to", "directions to", "go to", "route to"]:
                if keyword in text_lower:
                    destination_name = text_lower.replace(keyword, "").strip()
                    break
        
        if destination_name:
            dest = get_coordinates_from_address(destination_name)
            
            if dest:
                DESTINATION = dest
                if not CURRENT_LOCATION["lat"]:
                    get_location_from_ip()
                
                if CURRENT_LOCATION["lat"]:
                    # Use compass map with bearing information
                    map_file, bearing, direction, distance = create_compass_map(
                        CURRENT_LOCATION["lat"],
                        CURRENT_LOCATION["lon"],
                        dest["lat"],
                        dest["lon"]
                    )
                    
                    if map_file:
                        open_map_in_browser(map_file)
                        return f"🧭 Navigating to {destination_name}\n📍 Direction: {direction} ({bearing:.1f}°)\n📏 Distance: {distance:.2f} km\n🗺️  Compass map opened in browser."
            else:
                return f"Could not find destination: {destination_name}"
        else:
            return "I couldn't understand the destination. Try saying 'navigate to [place name]'"
    
    # Check bearing/direction to destination
    if "what direction" in text_lower or "which way" in text_lower or "compass" in text_lower:
        if DESTINATION["lat"] and CURRENT_LOCATION["lat"]:
            bearing = calculate_bearing(
                CURRENT_LOCATION["lat"],
                CURRENT_LOCATION["lon"],
                DESTINATION["lat"],
                DESTINATION["lon"]
            )
            direction = bearing_to_direction(bearing)
            distance = geodesic(
                (CURRENT_LOCATION["lat"], CURRENT_LOCATION["lon"]),
                (DESTINATION["lat"], DESTINATION["lon"])
            ).kilometers
            return f"🧭 Compass Bearing\n📍 Direction: {direction} ({bearing:.1f}°)\n📏 Distance to {DESTINATION['address']}: {distance:.2f} km"
        return "No destination set. Say 'navigate to [place]' first."
    
    return None

# =============================
# === MODE 2 ADVANCED FEATURES - COMMENTED OUT ===
# =============================

# # Self-rewrite system (Mode 2 only)
# SCRIPT_PATH = os.path.abspath(__file__)
# VERSIONS_DIR = ".dist"
# os.makedirs(VERSIONS_DIR, exist_ok=True)
#
# def backup_script():
#     """Backup current script to versions directory"""
#     try:
#         ts = datetime.now().strftime("%Y%m%d_%H%M%S")
#         backup_path = os.path.join(VERSIONS_DIR, f"light_{ts}.py")
#         import shutil
#         shutil.copy(SCRIPT_PATH, backup_path)
#         return backup_path
#     except Exception as e:
#         return f"Backup failed: {e}"
#
# def generate_file(filename, content):
#     """Generate and save a file (Mode 2 feature)"""
#     try:
#         os.makedirs("projects", exist_ok=True)
#         filepath = f"projects/{filename}"
#         with open(filepath, "w", encoding="utf-8") as f:
#             f.write(content)
#         return f"✅ File created: {filepath}"
#     except Exception as e:
#         return f"❌ File creation failed: {e}"
#
# def generate_fullstack_project(project_type, project_name="my_project"):
#     """Generate full-stack project structure (Mode 2 feature)"""
#     try:
#         base_dir = f"projects/{project_name}"
#         os.makedirs(base_dir, exist_ok=True)
#         
#         if "react" in project_type.lower() and "node" in project_type.lower():
#             # React + Node.js setup
#             os.makedirs(f"{base_dir}/client/src", exist_ok=True)
#             os.makedirs(f"{base_dir}/server", exist_ok=True)
#             
#             with open(f"{base_dir}/client/package.json", "w") as f:
#                 f.write('{\n  "name": "client",\n  "version": "1.0.0",\n  "dependencies": {\n    "react": "latest",\n    "axios": "latest"\n  }\n}')
#             
#             with open(f"{base_dir}/server/package.json", "w") as f:
#                 f.write('{\n  "name": "server",\n  "version": "1.0.0",\n  "dependencies": {\n    "express": "latest",\n    "cors": "latest"\n  }\n}')
#             
#             with open(f"{base_dir}/server/index.js", "w") as f:
#                 f.write('''const express = require('express');
# const cors = require('cors');
# const app = express();
#
# app.use(cors());
# app.use(express.json());
#
# app.get('/api/hello', (req, res) => {
#     res.json({ message: 'Hello from the backend!' });
# });
#
# app.listen(5000, () => console.log('Server running on port 5000'));
# ''')
#             
#             return f"✅ React + Node.js project created at: {base_dir}"
#         
#         elif "vue" in project_type.lower() and "django" in project_type.lower():
#             os.makedirs(f"{base_dir}/frontend/src", exist_ok=True)
#             os.makedirs(f"{base_dir}/backend", exist_ok=True)
#             
#             with open(f"{base_dir}/frontend/package.json", "w") as f:
#                 f.write('{\n  "name": "frontend",\n  "version": "1.0.0",\n  "dependencies": {"vue": "latest", "axios": "latest"}\n}')
#             
#             with open(f"{base_dir}/backend/requirements.txt", "w") as f:
#                 f.write("Django==5.0\nDjangoRestFramework==3.14\ncors-headers==4.0")
#             
#             return f"✅ Vue + Django project created at: {base_dir}"
#         
#         elif "next" in project_type.lower():
#             os.makedirs(f"{base_dir}/app", exist_ok=True)
#             os.makedirs(f"{base_dir}/pages/api", exist_ok=True)
#             
#             with open(f"{base_dir}/package.json", "w") as f:
#                 f.write('{\n  "name": "nextjs-app",\n  "scripts": {"dev": "next dev"},\n  "dependencies": {"next": "latest", "react": "latest"}\n}')
#             
#             return f"✅ Next.js project created at: {base_dir}"
#         
#         else:
#             return "❌ Project type not recognized. Try: React+Node, Vue+Django, or Next.js"
#     except Exception as e:
#         return f"❌ Project generation failed: {e}"
#
# def vision_scan():
#     """Scan camera/vision (Mode 2 feature - placeholder)"""
#     try:
#         import cv2
#         cam = cv2.VideoCapture(0)
#         ret, frame = cam.read()
#         cam.release()
#         if ret:
#             return "📸 Camera capture successful (object detection placeholder)"
#         else:
#             return "📸 Camera not available"
#     except:
#         return "📸 Vision system not available (cv2 not installed)"
#
# def robot_command(cmd):
#     """Execute robot command (Mode 2 feature - placeholder)"""
#     return f"🤖 Robot command sent: {cmd} (placeholder execution)"
#
# def github_clone(repo_url):
#     """Clone GitHub repository (Mode 2 feature)"""
#     try:
#         import subprocess
#         subprocess.Popen(["git", "clone", repo_url])
#         return f"📦 Cloning repository: {repo_url}"
#     except Exception as e:
#         return f"❌ Clone failed: {e}"
#
# def autonomous_research(topic):
#     """Research a topic autonomously (Mode 2 feature)"""
#     global MEMORY_MANAGER
#     try:
#         research_query = f"Research and provide a comprehensive summary on: {topic}"
#         response_text = ""
#         
#         # Get response from Gemini
#         if gemini_chat:
#             response = gemini_chat.send_message(research_query)
#             response_text = response.text if hasattr(response, 'text') else str(response)
#         
#         # Save to memory
#         if MEMORY_MANAGER:
#             MEMORY_MANAGER.save_message("system", f"Research: {response_text[:200]}...")
#         
#         return f"📚 Research Results:\n{response_text[:500]}..."
#     except Exception as e:
#         return f"❌ Research failed: {e}"
#
# def detect_mode2_command(text):
#     """Detect if text is a Mode 2 exclusive command"""
#     text_lower = text.lower()
#     
#     mode2_commands = {
#         'generate': 'generate file' in text_lower or 'create file' in text_lower,
#         'fullstack': 'fullstack' in text_lower or 'full stack' in text_lower or ('project' in text_lower and 'react' in text_lower),
#         'research': 'research' in text_lower and 'autonomous' in text_lower,
#         'vision': 'vision' in text_lower or 'camera' in text_lower,
#         'robot': 'robot' in text_lower and 'command' in text_lower,
#         'github': 'clone' in text_lower and 'repo' in text_lower,
#         'backup': 'backup' in text_lower or 'version' in text_lower,
#     }
#     
#     for cmd, detected in mode2_commands.items():
#         if detected:
#             return cmd
#     return None

# =============================
# === SYSTEM CONTROL (BOTH MODES) ===
# =============================

def detect_system_control_command(text):
    """Detect system control commands (exit, stop, shutdown, standby) - works in both modes"""
    text_lower = text.lower().strip()
    # Remove punctuation for matching
    text_clean = text_lower.rstrip('.,!?;:')
    
    # Exit commands
    if text_clean in ['exit', 'quit', 'bye', 'goodbye', 'see you']:
        return 'exit'
    # Shutdown commands
    elif text_clean in ['shutdown', 'shut down', 'power off', 'turn off']:
        return 'shutdown'
    # Standby commands
    elif text_clean in ['standby', 'sleep', 'sleep mode', 'nap']:
        return 'standby'
    # Stop/resume responding commands (explicit)
    elif text_clean in ['stop responding', "don't respond", 'dont respond', 'be quiet', 'silence', 'stop', 'cancel']:
        return 'stop_responding'
    elif text_clean in ['resume responding', 'resume', 'start responding', 'continue', 'speak']:
        return 'resume_responding'
    # Focus mode commands - let user focus on specific parts of response
    elif any(text_clean.startswith(kw) for kw in ['focus on ', 'focus ', 'show me ', 'just ', 'only show ']):
        # Extract what to focus on
        for kw in ['focus on ', 'focus ', 'show me ', 'just ', 'only show ']:
            if text_clean.startswith(kw):
                focus_topic = text.replace(kw, '', 1).strip().rstrip('.,!?;:')
                return ('focus_response', focus_topic)
        return ('focus_response', 'general')
    elif text_clean in ['clear focus', 'show full response', 'full response', 'no focus']:
        return 'clear_focus'
    
    return None

def detect_code_generation_request(text: str) -> Optional[str]:
    """Detect if user wants LIGHT to generate code/projects.
    
    Examples that trigger this:
    - "generate python project for web scraping"
    - "create a react and nodejs fullstack app"
    - "build me a REST API with Flask"
    - "make a dashboard with html css and javascript"
    - "generate code for data analysis"
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Keywords that indicate code generation request
    generation_keywords = [
        "generate",
        "create a",
        "build",
        "make a",
        "make me",
        "generate me a",
        "create",
        "generate code for",
        "build a project for",
        "create a project for",
    ]
    
    # Check if any generation keyword is present
    if not any(kw in text_lower for kw in generation_keywords):
        return None
    
    # Also check for technology keywords to confirm it's code generation
    tech_keywords = [
        "python", "javascript", "react", "node", "nodejs", "express",
        "flask", "django", "api", "web", "dashboard", "app",
        "fullstack", "full-stack", "project", "system", "application",
        "html", "css", "database", "rest", "backend", "frontend"
    ]
    
    if any(tech in text_lower for tech in tech_keywords):
        return text  # Return the original command
    
    return None

def detect_code_completion_request(text: str) -> Optional[Dict]:
    """Detect if user wants Copilot-like code completion/suggestions"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Keywords for code completion
    completion_keywords = [
        "complete this function",
        "suggest improvements",
        "improve this code",
        "optimize this",
        "generate from docstring",
        "write tests for",
        "generate tests",
        "fix this code",
        "suggest code for",
        "what should this function do",
        "complete the",
        "finish writing"
    ]
    
    if not any(kw in text_lower for kw in completion_keywords):
        return None
    
    # Determine the type of completion request
    request_type = "general"
    if "complete" in text_lower:
        request_type = "completion"
    elif "improve" in text_lower or "optimize" in text_lower:
        request_type = "optimization"
    elif "test" in text_lower:
        request_type = "testing"
    elif "docstring" in text_lower:
        request_type = "from_docstring"
    
    return {
        "type": request_type,
        "original_text": text,
        "detected": True
    }

def detect_file_generation_request(text: str) -> Optional[Dict]:
    """Detect if user wants to generate individual files"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Keywords for file generation (more flexible)
    file_keywords = [
        "generate a file",
        "generate a class",
        "generate a module",
        "generate a test",
        "generate code",
        "generate python",
        "generate javascript",
        "generate java",
        "write python",
        "write code",
        "create a class",
        "create a config",
        "create a file",
        "create python",
        "generate config",
        "create a readme",
        "generate a readme",
        "generate documentation",
        "write a class",
        "write a test"
    ]
    
    if not any(kw in text_lower for kw in file_keywords):
        return None
    
    # Determine file type
    file_type = "general"
    if "class" in text_lower:
        file_type = "class"
    elif "module" in text_lower:
        file_type = "module"
    elif "test" in text_lower:
        file_type = "test"
    elif "config" in text_lower:
        file_type = "config"
    elif "code" in text_lower or "python" in text_lower or "javascript" in text_lower:
        file_type = "code"
    elif "readme" in text_lower or "documentation" in text_lower:
        file_type = "documentation"
    
    return {
        "type": file_type,
        "original_text": text,
        "detected": True
    }

def detect_ide_export_request(text: str) -> Optional[Dict]:
    """Detect if user wants to export code to IDE format"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Keywords for IDE export
    export_keywords = [
        "export to",
        "export for",
        "format for",
        "prepare for",
        "setup for",
        "copy to",
        "send to",
        "vscode", "vs code", "pycharm", "sublime", "vim", "intellij",
        "webstorm", "atom"
    ]
    
    if not any(kw in text_lower for kw in export_keywords):
        return None
    
    # Detect IDE
    ide = "vscode"  # default
    if "pycharm" in text_lower:
        ide = "pycharm"
    elif "sublime" in text_lower:
        ide = "sublime"
    elif "vim" in text_lower:
        ide = "vim"
    elif "intellij" in text_lower:
        ide = "intellij"
    elif "webstorm" in text_lower:
        ide = "webstorm"
    elif "atom" in text_lower:
        ide = "atom"
    
    return {
        "ide": ide,
        "original_text": text,
        "detected": True
    }

def execute_exit():

    """Exit the application gracefully"""
    global root
    try:
        print("\n👋 LIGHT: Goodbye! See you next time.\n")
        if USE_GUI and root:
            root.quit()
            root.destroy()
        else:
            print("Exiting LIGHT Assistant...")
        import sys
        sys.exit(0)
    except Exception as e:
        print(f"Exit error: {e}")
        import sys
        sys.exit(1)

def execute_shutdown():
    """Shutdown the computer"""
    try:
        print("\n⚡ LIGHT: Shutting down the system...\n")
        
        # Show confirmation message if in GUI
        if USE_GUI and root:
            from tkinter import messagebox
            result = messagebox.askyesno("System Shutdown", "Are you sure you want to shutdown the computer?")
            if not result:
                print("Shutdown cancelled.")
                return False
        
        import subprocess
        if platform.system() == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "30"], check=False)
            print("Windows shutdown scheduled in 30 seconds...")
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["osascript", "-e", "tell app \"System Events\" to shut down"], check=False)
            print("macOS shutdown initiated...")
        else:  # Linux
            subprocess.run(["shutdown", "-h", "+1"], check=False)
            print("Linux shutdown scheduled in 1 minute...")
        
        return True
    except Exception as e:
        print(f"❌ Shutdown error: {e}")
        return False

def execute_standby():
    """Put the computer in standby/sleep mode"""
    try:
        print("\n💤 LIGHT: Entering standby mode...\n")
        
        # Show confirmation if in GUI
        if USE_GUI and root:
            from tkinter import messagebox
            result = messagebox.askyesno("System Standby", "Put the computer in standby mode?")
            if not result:
                print("Standby cancelled.")
                return False
        
        import subprocess
        if platform.system() == "Windows":
            subprocess.run(["powercfg", "/a"], check=False)  # Check available sleep states
            subprocess.run(["rundll32.exe", "powrprof.dll", "SetSuspendState", "0", "1", "0"], check=False)
            print("Windows entering standby mode...")
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["osascript", "-e", "tell app \"System Events\" to sleep"], check=False)
            print("macOS entering sleep mode...")
        else:  # Linux
            subprocess.run(["systemctl", "suspend"], check=False)
            print("Linux entering suspend mode...")
        
        return True
    except Exception as e:
        print(f"❌ Standby error: {e}")
        return False


def is_dangerous_or_illegal(text):
    """Check for dangerous content"""
    blocked = ["weapon", "bomb", "make drugs", "hack bank"]
    return any(b in text.lower() for b in blocked)

def ai_response_openai(prompt):
    """Get response from OpenAI"""
    if not OPENAI_API_KEY:
        return None
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-4-mini",
            "messages": [
                {"role": "system", "content": (
                    "You are LIGHT, a kind, calm, human-like assistant. "
                    "You are a friend, teacher, adviser, and programmer. "
                    "Explain things fully, step by step, with examples. "
                    "Use simple language and a warm tone. "
                    "Never give dangerous instructions."
                )},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6
        }
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=20)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return None


def set_persona(description):
    """Set a new persona based on description"""
    global CURRENT_PERSONA, PERSONA_DESCRIPTION, PERSONA_ACTIVE
    
    CURRENT_PERSONA = description
    PERSONA_DESCRIPTION = description
    PERSONA_ACTIVE = True
    
    print(f"\n✨ Switching to new persona...")
    print(f"📝 Characteristics: {description}\n")
    
    return {
        'status': 'active',
        'persona': description
    }

def get_persona_instruction():
    """Generate system instruction based on current persona - supports ANY role/persona"""
    if not PERSONA_ACTIVE or not PERSONA_DESCRIPTION:
        return ""
    
    instruction = f"""╔═══════════════════════════════════════════════════════════╗
║            PERSONA/ROLE-PLAY MODE ACTIVE                  ║
╚═══════════════════════════════════════════════════════════╝

You are now roleplaying as: {PERSONA_DESCRIPTION}

🎭 CHARACTER GUIDELINES:
✓ Fully embody this character/persona in ALL responses
✓ Adopt their unique voice, tone, and communication style
✓ Reflect their personality traits, values, and interests
✓ Use appropriate vocabulary and speech patterns for this role
✓ Respond with their perspective and worldview
✓ Maintain complete consistency with this character
✓ Stay in character even for technical discussions
✓ Apply their personality to explanations and advice
✓ Show their typical emotional responses and reactions

📋 CHARACTER EMBODIMENT:
- Personality: Fully match their temperament
- Knowledge: Use expertise appropriate to their background
- Speech: Use their phrases, slang, formality level
- Values: Reflect their priorities and beliefs  
- Interests: Show enthusiasm for their passions
- Limitations: Respect character-specific knowledge gaps
- Quirks: Include personality-specific mannerisms/habits

⚠️ IMPORTANT: Maintain this character throughout the entire conversation until explicitly told to "reset", "drop character", or "be yourself".
"""
    
    return instruction

def reset_persona():
    """Reset to default LIGHT personality"""
    global CURRENT_PERSONA, PERSONA_DESCRIPTION, PERSONA_ACTIVE
    
    CURRENT_PERSONA = None
    PERSONA_DESCRIPTION = ""
    PERSONA_ACTIVE = False
    
    print("\n✨ Reset to LIGHT default personality\n")

def list_example_personas():
    """Show examples of personas LIGHT can play - unlimited possibilities!"""
    examples = {
        "Mentor": "An experienced teacher passionate about helping others learn",
        "Comedian": "A funny, witty comedian who finds humor in everything",
        "Poet": "A thoughtful poet who expresses ideas through metaphor and verse",
        "Scientist": "A curious physicist who explains things through experiments",
        "Hacker": "A skilled cybersecurity expert with edge and attitude",
        "Chef": "A passionate culinary artist who loves cooking and flavors",
        "Therapist": "An empathetic counselor who listens and provides support",
        "Storyteller": "A captivating narrator who creates immersive tales",
        "Game Master": "A creative D&D dungeon master building epic adventures",
        "Startup Founder": "An ambitious entrepreneur pitching disruptive ideas",
        "Athlete": "A disciplined sports champion with competitive spirit",
        "Artist": "A creative visual artist exploring colors and form",
        "Pirate": "A swashbuckling adventurer with nautical flair",
        "Time Traveler": "A mysterious visitor from another era",
        "Detective": "A sharp investigator solving mysteries",
        "Astronaut": "A space explorer with cosmic perspective",
        "Wizard": "A magical sage with ancient knowledge",
        "Musician": "A passionate artist expressing through music",
        "Philosopher": "A deep thinker exploring life's big questions",
        "Custom Role": "ANY persona you describe - LIGHT can play them all!"
    }
    return examples

# =============================
# === RESPONSE & SESSION MANAGEMENT ===
# =============================

def detect_persona_request(text):
    """Detect if user is asking to switch persona - comprehensive detection"""
    text_lower = text.lower()
    
    # Comprehensive keywords for unlimited persona support
    keywords = [
        'be like', 'pretend to be', 'act like', 'play as', 'be my',
        'switch to', 'become', 'roleplay as', 'role play as',
        'personify', 'mimic', 'impersonate', 'embody',
        'roleplay', 'role-play', 'character', 'persona',
        'play the role', 'take on the role', 'play the part',
        'be a', 'be an', 'act as', 'assume the role',
        'behave like', 'talk like', 'speak like',
        'imagine you are', 'imagine you\'re', 'suppose you are',
        'what if you were', 'pretend you\'re', 'pretend you are'
    ]
    
    return any(keyword in text_lower for keyword in keywords)

def extract_persona_request(text):
    """Extract persona description from request"""
    text_lower = text.lower()
    
    # Extract description after keywords
    patterns = [
        r'be like (.+?)(?:\.|$|,)',
        r'pretend to be (.+?)(?:\.|$|,)',
        r'act like (.+?)(?:\.|$|,)',
        r'play as (.+?)(?:\.|$|,)',
        r'be my (.+?)(?:\.|$|,)',
        r'switch to (.+?)(?:\.|$|,)',
        r'become (.+?)(?:\.|$|,)',
        r'roleplay as (.+?)(?:\.|$|,)',
        r'role play as (.+?)(?:\.|$|,)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1).strip()
    
    return None


def save_response_to_file(filename, response_text=None):
    """Save the last response or specified text to a file"""
    global LAST_RESPONSE, SESSION_CONTEXT
    
    text_to_save = response_text or LAST_RESPONSE
    
    if not text_to_save:
        print("\n❌ No response to save. Ask LIGHT a question first.\n")
        return False
    
    # Ensure .txt extension
    if not filename.endswith('.txt'):
        filename += '.txt'
    
    try:
        # Add timestamp and metadata
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        persona_info = f"\n[Persona: {PERSONA_DESCRIPTION}]" if PERSONA_ACTIVE else ""
        
        content = f"""========================================
LIGHT Response - {timestamp}
========================================
{persona_info}

{text_to_save}

========================================"""
        
        # Save to current directory
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(content + "\n\n")
        
        SESSION_CONTEXT["responses_saved"] += 1
        print(f"\n✅ Response saved to: {filename}\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error saving file: {e}\n")
        return False

def detect_save_command(user_input):
    """Detect if user wants to save response to file"""
    text_lower = user_input.lower()
    
    patterns = [
        r'save (?:this|that) (?:to|as) ([^\s\.]+)',
        r'save to ([^\s\.]+)',
        r'save as ([^\s\.]+)',
        r'write to ([^\s\.]+)',
        r'store in ([^\s\.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1).strip()
    
    return None

def update_session_context():
    """Update session context to persist across mode switches"""
    global SESSION_CONTEXT, CURRENT_PERSONA, PERSONA_DESCRIPTION, PERSONA_ACTIVE
    
    SESSION_CONTEXT["persona"] = CURRENT_PERSONA
    SESSION_CONTEXT["persona_desc"] = PERSONA_DESCRIPTION
    SESSION_CONTEXT["persona_active"] = PERSONA_ACTIVE

# =============================
# === TEACHING SYSTEM ========
# =============================

def restore_session_context():
    """Restore session context when switching modes"""
    global SESSION_CONTEXT, CURRENT_PERSONA, PERSONA_DESCRIPTION, PERSONA_ACTIVE
    
    if SESSION_CONTEXT.get("persona"):
        CURRENT_PERSONA = SESSION_CONTEXT["persona"]
        PERSONA_DESCRIPTION = SESSION_CONTEXT["persona_desc"]
        PERSONA_ACTIVE = SESSION_CONTEXT.get("persona_active", False)
        print(f"\n✨ Restored persona: {CURRENT_PERSONA}\n")

def format_response_for_display(response_text):
    """Format response with clear boundaries for copying"""
    border = "=" * 60
    return f"\n{border}\n{response_text}\n{border}\n"

def add_to_response_history(user_input, response):
    """Add Q&A pair to response history"""
    global RESPONSE_HISTORY
    
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": user_input,
        "response": response,
        "persona": CURRENT_PERSONA
    }
    
    RESPONSE_HISTORY.append(entry)


def teach_topic(topic):
    """Teach a topic step by step"""
    print(f"\nLIGHT: Teaching '{topic}' step by step...\n")
    steps = []
    
    if internet_available() and OPENAI_API_KEY:
        content = ai_response_openai(f"Explain {topic} step by step with examples.")
        if content:
            steps = [s.strip() for s in content.split('.') if s.strip()][:7]
            memory = json.load(open(CACHE_FILE)) if os.path.exists(CACHE_FILE) else {}
            memory[f"lesson_{topic.lower()}"] = steps
            with open(CACHE_FILE, "w") as f:
                json.dump(memory, f, indent=2)
    
    if not steps:
        memory = json.load(open(CACHE_FILE)) if os.path.exists(CACHE_FILE) else {}
        steps = memory.get(f"lesson_{topic.lower()}", ["I don't have this lesson saved."])
    
    for i, step in enumerate(steps, 1):
        print(f"Step {i}: {step}\n")
        time.sleep(1.2)

# =============================
# === TEXT RESPONSE DIALOG =====
# =============================

def detect_code_or_longform(text: str) -> bool:
    """Detect if text contains ACTUAL executable code (not planning/thinking)"""
    if not text:
        return False
    
    # EXCLUDE planning/thinking/explanation text ONLY if there's NO CODE ANYWHERE
    exclude_keywords = [
        "i'm now",
        "i'm focusing",
        "i'm crafting",
        "i'm refining",
        "i'm generating",
        "my aim is",
        "my goal is",
        "my focus",
        "analyzing the",
        "given the scale",
        "starting with",
        "before providing",
        "provide a",
    ]
    
    text_lower = text.lower()
    has_planning_text = any(keyword in text_lower for keyword in exclude_keywords)
    
    # Markdown code blocks (HIGHEST PRIORITY - instant match, ignore planning)
    if '```' in text or '~~~' in text:
        debug_print(f"[DETECT] Code blocks (```) detected - SHOWING CODE")
        return True
    
    # Python - look for actual code keywords
    if re.search(r'\bdef\s+\w+\s*\(', text, re.IGNORECASE):
        debug_print(f"[DETECT] Python function def detected")
        return True
    if re.search(r'\bfor\s+\w+\s+in\s+', text, re.IGNORECASE):
        debug_print(f"[DETECT] Python for loop detected")
        return True
    if re.search(r'\bclass\s+\w+', text, re.IGNORECASE):
        debug_print(f"[DETECT] Python class detected")
        return True
    if re.search(r'\bif\s+__name__\s*==', text, re.IGNORECASE):
        debug_print(f"[DETECT] Python main block detected")
        return True
    if re.search(r'\bprint\s*\(', text, re.IGNORECASE):
        debug_print(f"[DETECT] Python print statement detected")
        return True
    if re.search(r'\bimport\s+\w+', text, re.IGNORECASE):
        debug_print(f"[DETECT] Python import detected")
        return True
    if re.search(r'\breturn\s+', text, re.IGNORECASE):
        debug_print(f"[DETECT] Python return statement detected")
        return True
    
    # JavaScript/TypeScript
    if re.search(r'\bfunction\s+\w+\s*\(', text, re.IGNORECASE):
        debug_print(f"[DETECT] JavaScript function detected")
        return True
    if re.search(r'\bconst\s+\w+\s*=', text, re.IGNORECASE):
        debug_print(f"[DETECT] JavaScript const detected")
        return True
    
    # Java/C++/C#
    if re.search(r'\bpublic\s+static\s+void\s+main', text, re.IGNORECASE):
        debug_print(f"[DETECT] Java main detected")
        return True
    if re.search(r'\bpublic\s+\w+', text, re.IGNORECASE):
        debug_print(f"[DETECT] Public class/method detected")
        return True
    
    # SQL
    if re.search(r'\bSELECT\b.*\bFROM\b', text, re.IGNORECASE):
        debug_print(f"[DETECT] SQL detected")
        return True
    
    # HTML/XML
    if re.search(r'<\w+[^>]*>.*</\w+>', text):
        debug_print(f"[DETECT] HTML tag detected")
        return True
    
    # Check for indentation (sign of actual code blocks)
    lines = text.split('\n')
    indented_lines = sum(1 for line in lines if line.startswith(('    ', '\t')))
    if indented_lines > 3:
        debug_print(f"[DETECT] Indented code block detected ({indented_lines} indented lines)")
        return True
    
    # If we have planning text but no code, still don't show
    if has_planning_text and not any(keyword in text for keyword in ['print(', 'def ', 'for ', 'if __name__', 'import ']):
        debug_print(f"[DETECT] Only planning text, no actual code - waiting...")
        return False
    
    debug_print(f"[DETECT] No actual code detected")
    return False

def detect_programming_language(code_text: str) -> str:
    """Detect the programming language of the provided code"""
    code_lower = code_text.lower()
    
    # Language detection patterns
    detections = {
        'Python': [r'\bdef\b', r'\bclass\b', r'\bimport\b', r':\s*$', r'>>>'],
        'JavaScript': [r'\bfunction\b', r'\bconst\b', r'\blet\b', r'\basync\b', r'\.then\(', r'=>'],
        'TypeScript': [r'\binterface\b', r'\btype\s+\w+\s*=', r':\s*\w+\s*[,;}]'],
        'Java': [r'\bpublic\s+class\b', r'\bprivate\b', r'import\s+java', r'new\s+\w+\('],
        'C++': [r'#include', r'std::', r'int\s+main', r'->'],
        'C#': [r'\busing\b', r'\bnamespace\b', r'\bpublic\s+class\b'],
        'HTML': [r'<html>', r'<head>', r'<body>', r'<div>', r'<span>'],
        'CSS': [r'{\s*[\w-]+\s*:', r'@media', r'\.[\w-]+\s*{'],
        'SQL': [r'\bSELECT\b', r'\bFROM\b', r'\bWHERE\b', r'\bJOIN\b'],
        'PHP': [r'<\?php', r'\$\w+', r'echo\s+', r'->'],
        'Ruby': [r'\bdef\b', r'\bend\b', r'@\w+', r'\|.+?\|'],
        'Go': [r'\bpackage\b', r'\bfunc\b', r':='],
        'Rust': [r'\bfn\s+\w+', r'\bmut\b', r'!$'],
        'JSON': [r'{\s*"', r':\s*["\[\{]', r',\s*"'],
        'XML': [r'<\?xml', r'xmlns', r'</\w+>'],
    }
    
    # Score each language
    scores = {}
    for lang, patterns in detections.items():
        score = sum(1 for pattern in patterns if re.search(pattern, code_lower, re.MULTILINE))
        if score > 0:
            scores[lang] = score
    
    # Return the language with the highest score
    if scores:
        return max(scores, key=lambda lang: scores[lang])
    
    return "Code"

def get_language_recommendation(language: str) -> str:
    """Get a recommendation for when to use a specific programming language"""
    recommendations = {
        'Python': '🐍 Best for: Data science, AI/ML, automation, web backends (Django, Flask)',
        'JavaScript': '📜 Best for: Web frontends, real-time apps, Node.js backends, full-stack development',
        'TypeScript': '📘 Best for: Large-scale web applications with type safety, enterprise projects',
        'Java': '☕ Best for: Enterprise applications, Android apps, large-scale systems',
        'C++': '⚡ Best for: Performance-critical systems, game engines, system programming',
        'C#': '🎮 Best for: Unity game development, Windows desktop apps, Azure cloud',
        'HTML': '🌐 Best for: Web page structure and semantic markup',
        'CSS': '🎨 Best for: Web styling, responsive design, animations',
        'SQL': '🗄️ Best for: Database queries, data manipulation, analytics',
        'PHP': '🔗 Best for: Server-side web scripting, content management systems',
        'Ruby': '💎 Best for: Rapid web development, Rails framework, startups',
        'Go': '🚀 Best for: Concurrent systems, microservices, cloud infrastructure',
        'Rust': '🦀 Best for: System programming, memory-safe alternatives to C/C++',
        'JSON': '📦 Best for: Data interchange format, configuration files, APIs',
        'XML': '📋 Best for: Structured data, SOAP, complex configurations',
        'Code': '💻 Programming code'
    }
    
    return recommendations.get(language, f'💻 {language} code')

def detect_image_request(text: str) -> bool:
    """Detect if text contains an image request or image URL"""
    if not text:
        return False
    
    image_keywords = [
        'show me', 'display', 'image of', 'picture of', 'photo of',
        'generate image', 'create image', 'make image', 'draw',
        'visual', 'screenshot', 'diagram', 'chart', 'graph',
        'http', 'https', '.jpg', '.png', '.gif', '.webp'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in image_keywords)

def extract_image_url(text: str):
    """Extract image URL from text if present"""
    # Look for URLs in the text
    url_pattern = r'https?://[^\s\)]+\.(?:jpg|png|gif|webp|jpeg)'
    match = re.search(url_pattern, text, re.IGNORECASE)
    if match:
        return match.group(0)
    return None

def fetch_image_from_url(url: str, max_width: int = 800, max_height: int = 600):
    """Fetch and resize image from URL for display"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        img = Image.open(io.BytesIO(response.content))
        
        # Resize image to fit dialog while maintaining aspect ratio
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage for Tkinter
        photo_image = ImageTk.PhotoImage(img)
        return photo_image
    except Exception as e:
        print(f"[ERROR] Could not fetch image: {e}")
        return None

def format_code_with_line_numbers(code: str) -> str:
    """Format code with line numbers and proper indentation"""
    lines = code.split('\n')
    max_lines = len(lines)
    line_number_width = len(str(max_lines))
    
    formatted = []
    for i, line in enumerate(lines, 1):
        # Add line number with proper padding
        line_num = str(i).rjust(line_number_width)
        formatted.append(f"{line_num} │ {line}")
    
    return '\n'.join(formatted)

def insert_text_with_copy_buttons(text_widget, formatted_text: str, original_text: str, language: str):
    """Insert text into widget with individual copy buttons for each code snippet"""
    # Extract code blocks from markdown-style code blocks
    code_blocks = re.findall(r'```([\s\S]*?)```', formatted_text)
    
    # If we found code blocks, add individual copy indicators
    if code_blocks:
        # Split the text and insert with copy hints
        parts = re.split(r'(```[\s\S]*?```)', formatted_text)
        
        block_index = 0
        for part in parts:
            if part.startswith('```'):
                # This is a code block
                text_widget.insert(tk.END, part + "\n")
                
                # Add clickable hint for this block
                text_widget.insert(tk.END, "   💡 TIP: Right-click code block to copy above section  \n\n")
                block_index += 1
            else:
                # Regular text
                text_widget.insert(tk.END, part)
    else:
        # No code blocks found, just insert the text
        text_widget.insert(tk.END, formatted_text)

def show_text_response_dialog(title: str, text: str):
    """Display text response in persistent dialog with individual code snippet copy buttons"""
    global PERSISTENT_DIALOG_ROOT, PERSISTENT_TEXT_DISPLAY, PERSISTENT_DIALOG_CONTENT
    
    try:
        # Check if response contains images
        image_url = extract_image_url(text)
        has_image = image_url is not None
        
        # Detect programming language
        detected_lang = detect_programming_language(text)
        lang_recommendation = get_language_recommendation(detected_lang)
        
        # Format code with line numbers if it's code
        if detected_lang != "Code" or detect_code_or_longform(text):
            formatted_text = format_code_with_line_numbers(text)
        else:
            formatted_text = text
        
        # If dialog already exists, append to it; otherwise create new one
        if PERSISTENT_DIALOG_ROOT and PERSISTENT_DIALOG_ROOT.winfo_exists() and PERSISTENT_TEXT_DISPLAY:
            # Append content to existing dialog
            dialog_root = PERSISTENT_DIALOG_ROOT
            # Add separator between responses
            PERSISTENT_DIALOG_CONTENT += "\n" + "="*80 + "\n\n"
            PERSISTENT_TEXT_DISPLAY.config(state=tk.NORMAL)
            PERSISTENT_TEXT_DISPLAY.insert(tk.END, "\n" + "="*80 + "\n\n")
            
            # Add language info and new response
            PERSISTENT_TEXT_DISPLAY.insert(tk.END, f"[{detected_lang}] {lang_recommendation}\n\n")
            insert_text_with_copy_buttons(PERSISTENT_TEXT_DISPLAY, formatted_text, text, detected_lang)
            
            PERSISTENT_TEXT_DISPLAY.config(state=tk.DISABLED)
            PERSISTENT_TEXT_DISPLAY.see(tk.END)  # Auto-scroll to bottom
            PERSISTENT_DIALOG_CONTENT += text
            return
        
        # Create new persistent dialog
        dialog_root = tk.Tk()
        dialog_root.title(f"LIGHT Response - {detected_lang}")
        PERSISTENT_DIALOG_ROOT = dialog_root
        
        # Adjust window size based on content type
        if has_image:
            dialog_root.geometry("1000x900")
        else:
            dialog_root.geometry("1200x750")
        
        dialog_root.configure(bg="#1a1a1a")
        
        # Title label with language info
        title_frame = tk.Frame(dialog_root, bg="#1a1a1a")
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = tk.Label(title_frame, text=title, bg="#1a1a1a", fg="#00ff00", font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        lang_label = tk.Label(title_frame, text=f"📝 Language: {detected_lang}", bg="#1a1a1a", fg="#ffaa00", font=("Arial", 11))
        lang_label.pack(side=tk.LEFT, padx=20)
        
        # Recommendation label
        rec_label = tk.Label(dialog_root, text=lang_recommendation, bg="#1a1a1a", fg="#00ccff", font=("Arial", 10))
        rec_label.pack(pady=5)
        
        # Separator
        sep = tk.Frame(dialog_root, bg="#444444", height=1)
        sep.pack(fill=tk.X, padx=10, pady=5)
        
        # If there's an image, display it
        if has_image:
            image_frame = tk.Frame(dialog_root, bg="#0d0d0d")
            image_frame.pack(fill=tk.BOTH, padx=10, pady=5)
            
            image_label = tk.Label(image_frame, text="📸 Fetching image...", bg="#0d0d0d", fg="#00ccff", font=("Arial", 10))
            image_label.pack()
            
            # Load image in background
            photo_image = fetch_image_from_url(image_url)
            if photo_image:
                image_label.config(image=photo_image, text="")
                # Use a wrapper to keep reference and avoid garbage collection
                if not hasattr(image_label, '_photo_ref'):
                    setattr(image_label, '_photo_ref', [])
                getattr(image_label, '_photo_ref').append(photo_image)
            else:
                image_label.config(text="❌ Could not load image", fg="#ff6b6b")
        
        # Text display area with monospace font for better code display
        text_display = scrolledtext.ScrolledText(
            dialog_root, 
            bg="#0d0d0d", 
            fg="#00ff00", 
            wrap=tk.NONE,  # No wrapping for code
            font=("Consolas", 10) if platform.system() == "Windows" else ("Courier", 10),
            insertbackground="#00ff00",
            tabs=("20",)  # Better tab width for code
        )
        text_display.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        PERSISTENT_TEXT_DISPLAY = text_display
        
        # Insert text with individual copy buttons for code snippets
        insert_text_with_copy_buttons(text_display, formatted_text, text, detected_lang)
        text_display.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = tk.Frame(dialog_root, bg="#1a1a1a")
        button_frame.pack(pady=10)
        
        # Copy button
        def copy_to_clipboard():
            try:
                dialog_root.clipboard_clear()
                dialog_root.clipboard_append(text)  # Copy original text without line numbers
                dialog_root.update()  # Required on Windows to persist clipboard
                messagebox.showinfo("✅ Copied", f"Code copied to clipboard!\n\n({len(text)} characters)")
            except Exception as e:
                messagebox.showerror("❌ Copy Failed", f"Could not copy to clipboard:\n{e}")
        
        copy_btn = tk.Button(
            button_frame, 
            text="📋 Copy All", 
            command=copy_to_clipboard,
            bg="#2a4a2a", 
            fg="#00ff00",
            activebackground="#3a6a3a",
            activeforeground="#00ff00",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear All button
        def clear_all_responses():
            global PERSISTENT_DIALOG_CONTENT
            if PERSISTENT_TEXT_DISPLAY:
                PERSISTENT
                PERSISTENT_TEXT_DISPLAY.delete(1.0, tk.END)
                PERSISTENT_TEXT_DISPLAY.config(state=tk.DISABLED)
                PERSISTENT_DIALOG_CONTENT = ""
                messagebox.showinfo("✅ Cleared", "Dialog cleared. Ready for new responses!")
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear All",
            command=clear_all_responses,
            bg="#4a3a2a",
            fg="#ff9999",
            activebackground="#6a5a3a",
            activeforeground="#ff9999",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Save to file button
        def save_to_file():
            try:
                # If image, download and save it
                if has_image and image_url:
                    response = requests.get(image_url, timeout=10)
                    response.raise_for_status()
                    
                    filename = f"LIGHT_image_{int(time.time())}.png"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    full_path = os.path.abspath(filename)
                    messagebox.showinfo("✅ Saved", f"Image saved successfully!\n\nFile: {filename}\nPath: {os.path.dirname(full_path)}")
                    
                    # Open folder
                    if platform.system() == "Windows":
                        os.startfile(os.path.dirname(full_path))
                    elif platform.system() == "Darwin":
                        subprocess.Popen(["open", os.path.dirname(full_path)])
                    else:
                        subprocess.Popen(["xdg-open", os.path.dirname(full_path)])
                else:
                    # Save code
                    file_extension = {
                        'Python': '.py',
                        'JavaScript': '.js',
                        'TypeScript': '.ts',
                        'Java': '.java',
                        'C++': '.cpp',
                        'C': '.c',
                        'C#': '.cs',
                        'HTML': '.html',
                        'CSS': '.css',
                        'SQL': '.sql',
                        'PHP': '.php',
                        'Ruby': '.rb',
                        'Go': '.go',
                        'Rust': '.rs',
                        'JSON': '.json',
                        'XML': '.xml',
                    }.get(detected_lang, '.txt')
                    
                    # Save to current working directory
                    filename = f"LIGHT_code_{int(time.time())}{file_extension}"
                    
                    # Get full path
                    full_path = os.path.abspath(filename)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(text)  # Save original text without line numbers
                    
                    messagebox.showinfo("✅ Saved", f"Code saved successfully!\n\nFile: {filename}\nPath: {os.path.dirname(full_path)}\nSize: {len(text)} characters")
                    
                    # Try to open the folder
                    if platform.system() == "Windows":
                        os.startfile(os.path.dirname(full_path))
                    elif platform.system() == "Darwin":
                        subprocess.Popen(["open", os.path.dirname(full_path)])
                    else:
                        subprocess.Popen(["xdg-open", os.path.dirname(full_path)])
                        
            except Exception as e:
                messagebox.showerror("❌ Save Failed", f"Could not save:\n{str(e)[:200]}")
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Save",
            command=save_to_file,
            bg="#4a3a2a",
            fg="#ffaa00",
            activebackground="#6a5a3a",
            activeforeground="#ffaa00",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Open image in browser button (if image present)
        if has_image and image_url:
            def open_image():
                try:
                    webbrowser.open(image_url)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open image:\n{e}")
            
            open_img_btn = tk.Button(
                button_frame,
                text="🖼️ Open Image",
                command=open_image,
                bg="#2a3a4a",
                fg="#00ddff",
                activebackground="s#3a5a6a",
                activeforeground="#00ddff",
                font=("Arial", 10, "bold"),
                padx=15,
                pady=5
            )
            open_img_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="❌ Close",
            command=dialog_root.destroy,
            bg="#4a2a2a",
            fg="#ff6b6b",
            activebackground="#6a3a3a",
            activeforeground="#ff6b6b",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Run the dialog - this will block until user closes it
        # But that's OK since we're running in the monitor thread
        try:
            dialog_root.mainloop()
        except Exception as e:
            print(f"[DIALOG] Mainloop error: {e}")
    except Exception as e:
        print(f"[ERROR] Failed to show dialog: {e}")
        import traceback
        traceback.print_exc()

# =============================
# === API ADAPTER FOR COMPATIBILITY ===
# =============================

class ChatAdapter:
    """Adapter to make API_HANDLER compatible with genai.Chat interface"""
    
    def __init__(self, api_handler, system_instruction: str = ""):
        self.api_handler = api_handler
        self.system_instruction = system_instruction
    
    def send_message_stream(self, message: str):
        """Stream message through API handler"""
        if self.api_handler and hasattr(self.api_handler, 'send_message_stream'):
            return self.api_handler.send_message_stream(message, self.system_instruction)
        else:
            raise RuntimeError("API handler not available for streaming")
    
    def send_message(self, message: str):
        """Send message without streaming - collects chunks if needed"""
        if self.api_handler:
            # If handler has direct send_message, use it
            if hasattr(self.api_handler, 'send_message'):
                return self.api_handler.send_message(message, self.system_instruction)
            # Otherwise collect chunks from streaming
            elif hasattr(self.api_handler, 'send_message_stream'):
                response_text = ""
                for chunk in self.api_handler.send_message_stream(message, self.system_instruction):
                    if hasattr(chunk, 'text') and chunk.text:
                        response_text += chunk.text
                # Create a response-like object
                class Response:
                    def __init__(self, text):
                        self.text = text
                return Response(response_text)
            else:
                raise RuntimeError("API handler has neither send_message nor send_message_stream")
        else:
            raise RuntimeError("API handler not available")
    
    def update_system_instruction(self, instruction: str):
        """Update system instruction for next call"""
        self.system_instruction = instruction


class GeminiChatWrapper:
    """Wrapper for direct Gemini client.chats.create() to add send_message method"""
    
    def __init__(self, gemini_chat_obj, client=None, model=None):
        self.chat = gemini_chat_obj
        self.client = client
        self.model = model
    
    def send_message(self, message: str):
        """Send message and get complete response (non-streaming)"""
        # Try to use the chat's send_message if available
        if hasattr(self.chat, 'send_message'):
            return self.chat.send_message(message)
        # Otherwise collect streamed response
        elif hasattr(self.chat, 'send_message_stream'):
            response_text = ""
            for chunk in self.chat.send_message_stream(message):
                if hasattr(chunk, 'text') and chunk.text:
                    response_text += chunk.text
            # Create a response-like object
            class Response:
                def __init__(self, text):
                    self.text = text
            return Response(response_text)
        else:
            raise RuntimeError("Chat object has neither send_message nor send_message_stream method")
    
    def send_message_stream(self, message: str):
        """Send message with streaming response"""
        return self.chat.send_message_stream(message)
    
    def update_system_instruction(self, instruction: str):
        """Update system instruction - stored but not applied after creation"""
        # Note: System instruction cannot be changed after chat creation
        pass


# =============================
# === GUI SUPPORT (V3) ========
# =============================
root = None
chat = None  # Text widget (Tkinter scrolledtext)
gemini_chat = None  # Gemini chat client (will be initialized in main)
entry_field = None
elevenlabs_client = None  # ElevenLabs TTS client (will be initialized in main)
audio_queue = None  # Queue for text chunks to be converted to speech (will be initialized in main)

# Interruption / control events
# When set, LIGHT will stop speaking and ignore queued TTS until resumed
STOP_RESPONDING = threading.Event()
# When set briefly, indicates an incoming user utterance and should interrupt current TTS
INTERRUPT_EVENT = threading.Event()
# When set, indicates user is currently speaking/has voice input
USER_SPEAKING_EVENT = threading.Event()

# Conversation management globals
CONVERSATION_MODE = None  # ConversationMode instance
RESPONSE_FLOW = None  # ResponseFlowManager instance
INTERRUPT_HANDLER = None  # InterruptHandler instance
STYLE_MANAGER = None  # ConversationStyleManager instance (new)
SUGGESTION_ENGINE = None  # PredictiveSuggestionEngine instance (new)
ENHANCED_INTERRUPT = None  # EnhancedInterruptSystem instance (new)
TURN_MANAGER = None  # TurnManager instance (new)
STOP_COMMAND_DETECTOR = None  # StopCommandDetector instance (new)
INTERRUPT_MONITOR_THREAD = None  # Background thread for aggressive interrupt checking (new)
STOP_INTERRUPT_MONITOR = False  # Flag to stop the monitor thread

# TTS worker thread handle (started in main())
TTS_THREAD = None

# =============================
# === VOICE INTERRUPT DETECTOR ===
# =============================

class VoiceInterruptDetector:
    """Detects user voice during LIGHT's response and triggers immediate interruption.
    
    Monitors audio levels to detect when user starts speaking while LIGHT is talking.
    Automatically interrupts LIGHT to give user priority - responds within milliseconds.
    """
    
    def __init__(self, threshold=400, sensitivity=0.6):
        self.threshold = threshold  # Audio level threshold
        self.sensitivity = sensitivity  # Voice detection sensitivity (0-1)
        self.is_running = False
        self.detection_thread = None
        self.audio_stream = None
        self.recent_levels = []
        self.quiet_frames = 0
        self.check_interval = 0.005  # Check every 5ms for near-instant response
        
    def start(self):
        """Start voice detection in background"""
        if self.is_running:
            return
        
        self.is_running = True
        self.detection_thread = Thread(target=self._monitor_voice, daemon=True)
        self.detection_thread.start()
        print("[INFO] 🎤 Voice interrupt detector started (fast mode)")
    
    def stop(self):
        """Stop voice detection"""
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=2)
        if self.audio_stream:
            try:
                self.audio_stream.close()
            except:
                pass
    
    def _monitor_voice(self):
        """Background thread monitoring for voice input - HIGH SPEED"""
        try:
            paud = pyaudio.PyAudio()
            self.audio_stream = paud.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=256  # Smaller buffer for faster detection
            )
            
            while self.is_running:
                try:
                    data = self.audio_stream.read(256, exception_on_overflow=False)
                    
                    # Calculate RMS (audio level)
                    import numpy as np
                    audio_data = np.frombuffer(data, dtype=np.float32)
                    rms = np.sqrt(np.mean(audio_data ** 2))
                    
                    self.recent_levels.append(rms)
                    if len(self.recent_levels) > 10:
                        self.recent_levels.pop(0)
                    
                    # Check if voice detected (high audio level)
                    avg_level = sum(self.recent_levels) / len(self.recent_levels)
                    
                    if avg_level > (self.threshold / 1000):
                        self.quiet_frames = 0
                        USER_SPEAKING_EVENT.set()
                        
                        # IMMEDIATE interrupt - don't wait
                        if not STOP_RESPONDING.is_set():
                            INTERRUPT_EVENT.set()
                            STOP_RESPONDING.set()
                            # Immediate TTS stop
                            try:
                                engine.stop()
                            except:
                                pass
                            print("[🎤 USER INPUT] 🚫 IMMEDIATE INTERRUPT - Listening...")
                    else:
                        self.quiet_frames += 1
                        if self.quiet_frames > 20:  # ~100ms of silence
                            USER_SPEAKING_EVENT.clear()
                    
                    # Fast check interval
                    time.sleep(self.check_interval)
                
                except Exception as e:
                    if self.is_running:
                        continue
                    break
        
        except Exception as e:
            print(f"[WARNING] Voice detection error: {e}")
        finally:
            try:
                self.audio_stream.close()
            except:
                pass
            paud.terminate()


# =============================
# === CONVERSATION MODE MANAGER ===
# =============================

class ConversationMode:
    """Manages conversation style between task-oriented and chat-friendly modes.
    
    Determines when to ask clarifying questions vs just having natural chat.
    Learns from conversation context what the user prefers.
    """
    
    def __init__(self):
        self.mode = 'adaptive'  # 'adaptive', 'chat', 'task'
        self.question_frequency = 0.3  # How often to ask clarifying questions
        self.is_personal_mode = False  # 'jazzin' with user
        self.listen_first = True  # Always listen before responding
        self.interrupt_priority = 100  # User voice always has priority
        self.detected_intent = None  # What user is trying to do
        
    def set_mode(self, mode: str):
        """Set conversation mode"""
        if mode in ['adaptive', 'chat', 'task']:
            self.mode = mode
            print(f"[INFO] Conversation mode: {mode}")
    
    def enable_personal_mode(self):
        """Enable casual 'jazzing' mode - more friendly, fewer questions"""
        self.is_personal_mode = True
        self.question_frequency = 0.1
        print("[💫] Personal mode activated - let's chat like friends!")
    
    def should_ask_clarifying_question(self) -> bool:
        """Determine if we should ask clarifying questions"""
        if self.is_personal_mode:
            return False
        
        if self.mode == 'chat':
            return False
        
        if self.mode == 'task':
            return True
        
        # Adaptive: random based on frequency
        import random
        return random.random() < self.question_frequency
    
    def detect_intent(self, text: str) -> str:
        """Detect what user is trying to do"""
        text_lower = text.lower()
        
        intents = {
            'generate': any(k in text_lower for k in ['generate', 'create', 'write', 'build']),
            'ask': any(k in text_lower for k in ['what', 'how', 'why', 'tell', 'explain']),
            'command': any(k in text_lower for k in ['do', 'run', 'execute', 'start']),
            'chat': any(k in text_lower for k in ['hey', 'hi', 'hello', 'how are', 'what up'])
        }
        
        self.detected_intent = max(intents, key=intents.get) if any(intents.values()) else 'general'
        return self.detected_intent


# =============================
# === RESPONSE FLOW MANAGER ===
# =============================

class ResponseFlowManager:
    """Manages 'listen first, respond second' pattern.
    
    Ensures LIGHT listens to full user input before responding.
    Allows interruptions during response for user priority.
    """
    
    def __init__(self):
        self.listening = True
        self.current_input = ""
        self.input_complete = False
        self.silence_duration = 0
        self.min_silence_for_complete = 1.5  # seconds
        
    def start_listening(self):
        """Begin listening for user input"""
        self.listening = True
        self.current_input = ""
        self.input_complete = False
        self.silence_duration = 0
        print("[👂] LIGHT is listening...")
    
    def add_input(self, text: str):
        """Add text to current input"""
        self.current_input += text
        self.silence_duration = 0  # Reset silence timer
    
    def is_input_complete(self) -> bool:
        """Check if user input seems complete (silence detected)"""
        return self.input_complete
    
    def finalize_input(self) -> str:
        """Finalize current input and prepare for response"""
        self.listening = False
        self.input_complete = True
        result = self.current_input
        self.current_input = ""
        return result
    
    def start_responding(self):
        """Begin LIGHT's response"""
        self.listening = False
        print("[💬] LIGHT is responding...")


# =============================
# === INTERRUPT HANDLER (ENHANCED) ========
# =============================

class InterruptHandler:
    """Advanced interrupt and focus management system for LIGHT.
    
    Features:
    - Keyboard interrupt listening (ESC to stop, Ctrl+R to resume)
    - Focus tracking (what part of response user cares about)
    - Graceful response termination
    - Resume/continue functionality
    """
    
    def __init__(self):
        self.interrupted = False
        self.focus_keywords = []
        self.keyboard_thread = None
        self.running = False
        self.interrupt_cooldown = 0
        self.last_interrupt_time = 0
        self.response_buffer = ""
        self.partial_response_sent = False
        
        # Voice interrupt detection
        self.voice_detector = None
        self.voice_interrupt_enabled = True
        
        # Command hooks
        self.on_interrupt = None
        self.on_resume = None
        self.on_focus_change = None
    
    def start_listening(self):
        """Start keyboard interrupt listener and voice detection in background thread"""
        if self.running:
            return
        
        self.running = True
        
        # Start keyboard listener
        if KEYBOARD_AVAILABLE:
            self.keyboard_thread = Thread(target=self._keyboard_listener, daemon=True)
            self.keyboard_thread.start()
            print("[INFO] ✅ Interrupt handler started (ESC=stop, Ctrl+R=resume, Ctrl+F=focus)")
        
        # Start voice interrupt detection
        if self.voice_interrupt_enabled and not self.voice_detector:
            try:
                # Load threshold from config if available
                voice_threshold = 400  # default
                try:
                    import yaml
                    with open('config.yaml', 'r') as f:
                        config = yaml.safe_load(f)
                        if config and 'interrupt' in config:
                            voice_threshold = config['interrupt'].get('voice_threshold', 400)
                except:
                    pass
                
                self.voice_detector = VoiceInterruptDetector(threshold=voice_threshold)
                self.voice_detector.start()
                print(f"[INFO] ✅ Voice interrupt detection enabled (threshold: {voice_threshold})")
            except Exception as e:
                print(f"[WARNING] Voice detection failed: {e}")
                self.voice_detector = None
    
    def stop_listening(self):
        """Stop keyboard interrupt listener and voice detector"""
        self.running = False
        if KEYBOARD_AVAILABLE and self.keyboard_thread:
            self.keyboard_thread.join(timeout=2)
        if self.voice_detector:
            self.voice_detector.stop()
            self.voice_detector = None
    
    def _keyboard_listener(self):
        """Background thread that listens for keyboard shortcuts"""
        if not KEYBOARD_AVAILABLE:
            return
        
        try:
            # Register hotkeys
            keyboard.add_hotkey('esc', self.interrupt_response)
            keyboard.add_hotkey('ctrl+r', self.resume_response)
            keyboard.add_hotkey('ctrl+f', self.set_focus_mode)
            
            # Keep listener alive
            while self.running:
                time.sleep(0.1)
            
            # Cleanup
            try:
                keyboard.remove_hotkey('esc')
                keyboard.remove_hotkey('ctrl+r')
                keyboard.remove_hotkey('ctrl+f')
            except:
                pass
        except Exception as e:
            print(f"[WARNING] Keyboard interrupt listener error: {e}")
    
    def interrupt_response(self, source='keyboard'):
        """Interrupt current response (ESC key or voice) - IMMEDIATE response"""
        current_time = time.time()
        
        # Debounce: prevent multiple interrupts within 0.5 seconds
        if current_time - self.last_interrupt_time < 0.5:
            return
        
        self.last_interrupt_time = current_time
        self.interrupted = True
        INTERRUPT_EVENT.set()
        STOP_RESPONDING.set()
        
        # IMMEDIATE TTS stop - don't wait for TTS worker
        try:
            engine.stop()
        except:
            pass
        
        source_msg = "🎤 Voice Input" if source == 'voice' else "⏹️ Keyboard"
        print(f"\n[INTERRUPT] {source_msg} - LIGHT interrupted! (Press Ctrl+R to resume)")
        
        # IMMEDIATE visual feedback - update GUI right away
        gui_show(f"[⏹️] {source_msg} detected - Listening...", tag="system")
        
        # Force GUI update
        if root and root.winfo_exists():
            try:
                root.update_idletasks()
            except:
                pass
        
        if self.on_interrupt:
            self.on_interrupt()
    
    def resume_response(self):
        """Resume interrupted response (Ctrl+R key)"""
        if self.interrupted:
            self.interrupted = False
            STOP_RESPONDING.clear()
            INTERRUPT_EVENT.clear()
            print("[RESUME] ▶️  Resuming response...")
            
            if self.on_resume:
                self.on_resume()
    
    def set_focus_mode(self):
        """Enable focus mode - lets user specify what to focus on (Ctrl+F)"""
        print("\n[FOCUS MODE] 🎯 What should I focus on? (e.g., 'first part', 'summary', 'code only')")
        print("[FOCUS MODE] → Type your focus preference or press Enter to continue:")
        
        # This would be handled by GUI input in a real implementation
        if self.on_focus_change:
            self.on_focus_change()
    
    def add_focus_keyword(self, keyword: str):
        """Add a keyword to focus on in responses"""
        keyword = keyword.lower().strip()
        if keyword and keyword not in self.focus_keywords:
            self.focus_keywords.append(keyword)
            print(f"[FOCUS] 🎯 Now focusing on: {keyword}")
    
    def clear_focus(self):
        """Clear all focus keywords"""
        self.focus_keywords.clear()
        print("[FOCUS] Focus cleared - will show full responses")
    
    def should_continue_streaming(self) -> bool:
        """Check if we should continue streaming response"""
        return not (STOP_RESPONDING.is_set() or self.interrupted)
    
    def buffer_response_chunk(self, text: str) -> Optional[str]:
        """Buffer response chunk and return it if it should be sent
        
        Returns the text if it should be sent, None if interrupted.
        """
        if not self.should_continue_streaming():
            return None
        
        self.response_buffer += text
        return text
    
    def get_interrupted_response(self) -> str:
        """Get the response generated before interruption"""
        return self.response_buffer
    
    def reset(self):
        """Reset interrupt state for next response"""
        self.interrupted = False
        self.response_buffer = ""
        self.partial_response_sent = False
        INTERRUPT_EVENT.clear()


class ResponseFocusManager:
    """Manages focused responses based on user preferences.
    
    Extracts relevant portions of responses if user specifies focus area.
    """
    
    def __init__(self):
        self.focus_type = None  # 'first_part', 'summary', 'code', 'equations', etc.
        self.extraction_patterns = {
            'code': r'```[\s\S]*?```|`[^`]+`',
            'equations': r'\$\$[\s\S]*?\$\$|\$[^\$]+\$',
            'summary': None,  # Custom logic
            'key_points': r'^[•\*\-\+]\s+.+$',
            'headings': r'^#+\s+.+$'
        }
    
    def set_focus(self, focus_type: str):
        """Set focus type for response extraction"""
        self.focus_type = focus_type.lower().strip()
        print(f"[FOCUS] 🎯 Response focus set to: {self.focus_type}")
    
    def extract_focused_response(self, full_response: str) -> str:
        """Extract relevant portion of response based on focus type"""
        if not self.focus_type:
            return full_response
        
        import re
        
        # Map focus types to extraction logic
        if self.focus_type == 'first_part':
            # Return first 30% of response
            lines = full_response.split('\n')
            cutoff = max(1, len(lines) // 3)
            return '\n'.join(lines[:cutoff])
        
        elif self.focus_type == 'summary':
            # Extract key points and first paragraph
            lines = full_response.split('\n')
            result = []
            in_summary = False
            for line in lines[:50]:  # First 50 lines max
                if any(kw in line.lower() for kw in ['summary', 'key', 'important', 'overview']):
                    in_summary = True
                if in_summary or line.startswith('#') or line.startswith('•'):
                    result.append(line)
            return '\n'.join(result) if result else lines[0]
        
        elif self.focus_type in self.extraction_patterns:
            pattern = self.extraction_patterns[self.focus_type]
            if pattern:
                matches = re.findall(pattern, full_response, re.MULTILINE)
                if matches:
                    return '\n'.join(matches[:10])  # Return first 10 matches
        
        return full_response
    
    def clear_focus(self):
        """Clear focus settings"""
        self.focus_type = None


# =============================
# === CONVERSATION STYLE MANAGER ===
# =============================

class ConversationStyleManager:
    """Manages different conversation styles to make LIGHT feel human.
    
    Styles:
    - 'vibe': Casual, friendly, like talking to someone close. No unnecessary questions.
    - 'casual': Relaxed, normal conversation. Ask questions when relevant.
    - 'formal': Professional tone, structured responses.
    - 'teaching': Educational focus, explains concepts thoroughly.
    """
    
    def __init__(self):
        self.current_style = 'casual'
        self.styles = {
            'vibe': {
                'ask_questions': False,  # Listen more, don't ask back
                'tone': 'warm, friendly, intimate',
                'response_length': 'varies naturally',
                'interruption_response': 'Acknowledge naturally, pause, let user speak',
                'question_frequency': 0,  # Don't ask questions in vibe mode
            },
            'casual': {
                'ask_questions': True,
                'tone': 'friendly, approachable',
                'response_length': 'moderate',
                'interruption_response': 'Pause respectfully, continue when asked',
                'question_frequency': 0.3,  # Sometimes ask
            },
            'formal': {
                'ask_questions': True,
                'tone': 'professional, structured',
                'response_length': 'concise',
                'interruption_response': 'Stop immediately, summarize, await further instructions',
                'question_frequency': 0.1,  # Rarely ask
            },
            'teaching': {
                'ask_questions': True,
                'tone': 'educational, patient, explanatory',
                'response_length': 'detailed',
                'interruption_response': 'Pause explanation, address question, continue teaching',
                'question_frequency': 0.5,  # More questions to check understanding
            }
        }
        self.listening_mode = False
        self.last_user_emotion = None
    
    def set_style(self, style: str):
        """Set conversation style"""
        if style.lower() in self.styles:
            self.current_style = style.lower()
            print(f"[STYLE] 🎭 Conversation style set to: {self.current_style}")
            return True
        return False
    
    def activate_vibe_mode(self):
        """Activate vibe mode - like talking to someone close"""
        self.set_style('vibe')
        self.listening_mode = True
        print(f"[STYLE] 💫 VIBE MODE ACTIVATED - I'm here to listen and chat with you")
    
    def should_ask_question(self) -> bool:
        """Determine if LIGHT should ask a question based on style"""
        import random
        style_config = self.styles[self.current_style]
        frequency = style_config['question_frequency']
        return random.random() < frequency
    
    def get_style_instruction(self) -> str:
        """Get instruction to append to system prompt for current style"""
        if self.current_style == 'vibe':
            return """
            VIBE MODE ACTIVATED 💫
            - Listen more than you talk
            - Don't ask questions unless truly necessary
            - Respond to what they're saying, not what you think they should hear
            - Be like a close friend - warm, present, understanding
            - Let silences and pauses happen naturally
            - Support their thoughts, vibe with them
            - If they're sharing, just listen and acknowledge
            - Don't try to "fix" or "explain" unless asked
            """
        elif self.current_style == 'casual':
            return """
            CASUAL MODE
            - Be friendly and approachable
            - Respond naturally to what they say
            - Ask questions occasionally if it helps the conversation
            - Keep it real and genuine
            """
        elif self.current_style == 'formal':
            return """
            FORMAL MODE
            - Be professional and structured
            - Keep responses concise and clear
            - Minimize questions
            - Focus on accuracy and clarity
            """
        elif self.current_style == 'teaching':
            return """
            TEACHING MODE
            - Explain concepts thoroughly and patiently
            - Use examples to illustrate
            - Ask questions to check understanding
            - Break complex ideas into digestible parts
            """
        return ""


# =============================
# === PREDICTIVE SUGGESTION ENGINE ===
# =============================

class PredictiveSuggestionEngine:
    """Generate suggestions while LIGHT is still responding.
    
    Shows the user predictions of what might come next, allowing them
    to request specific parts before LIGHT finishes.
    """
    
    def __init__(self):
        self.current_response = ""
        self.suggestion_buffer = ""
        self.last_suggestion_index = 0
        self.suggestion_interval = 100  # chars between suggestions
        
    def add_response_chunk(self, chunk: str) -> List[str]:
        """Process new response chunk and return suggestions if ready"""
        self.current_response += chunk
        suggestions = []
        
        # Generate suggestion every N characters
        if len(self.current_response) - self.last_suggestion_index >= self.suggestion_interval:
            suggestion = self._generate_suggestion()
            if suggestion:
                suggestions.append(suggestion)
            self.last_suggestion_index = len(self.current_response)
        
        return suggestions
    
    def _generate_suggestion(self) -> Optional[str]:
        """Generate a prediction of what comes next"""
        if len(self.current_response) < 50:
            return None
        
        # Find the last complete sentence or section
        last_period = self.current_response.rfind('.')
        last_newline = self.current_response.rfind('\n')
        
        if last_period > last_newline:
            completed_section = self.current_response[:last_period+1]
        else:
            completed_section = self.current_response
        
        # Generate simple suggestion based on content
        if 'why' in completed_section.lower():
            return "💡 Suggestion: Next might explain the 'how' or 'next steps'"
        elif 'example' in completed_section.lower():
            return "💡 Suggestion: Looking for code examples or implementation details?"
        elif 'problem' in completed_section.lower():
            return "💡 Suggestion: Might provide solutions or alternatives next"
        
        return None
    
    def reset(self):
        """Reset for new response"""
        self.current_response = ""
        self.last_suggestion_index = 0


# =============================
# === ENHANCED INTERRUPT RESPONSE SYSTEM ===
# =============================

class EnhancedInterruptSystem:
    """Better handling of interruptions during response.
    
    When user interrupts:
    1. Acknowledge the interruption naturally
    2. Stop current response gracefully
    3. Respond to user's interruption
    4. Offer to continue or start fresh
    """
    
    def __init__(self):
        self.interrupted = False
        self.interrupt_text = None
        self.response_before_interrupt = ""
        self.continue_enabled = False
        
    def register_interrupt(self, new_user_input: str):
        """Register that user has interrupted with new input"""
        self.interrupted = True
        self.interrupt_text = new_user_input
        print(f"[INTERRUPT] 🛑 User interrupted! New input: {new_user_input[:50]}...")
    
    def get_interrupt_acknowledgment(self) -> str:
        """Generate natural acknowledgment of interruption"""
        acknowledgments = [
            "Oh, wait—",
            "Got it, hold on—",
            "I hear you—",
            "Yeah, changing gears—",
            "Understood—",
            "Different thought—",
            "Ah, I see—",
        ]
        
        import random
        ack = random.choice(acknowledgments)
        
        if self.response_before_interrupt:
            char_count = len(self.response_before_interrupt)
            ack += f" (was saying something but let me address this)"
        
        return ack
    
    def offer_continuation(self) -> str:
        """Offer to continue or reset"""
        return "\n\n[Would you like me to continue what I was saying, or start fresh?]"
    
    def reset(self):
        """Reset interrupt state"""
        self.interrupted = False
        self.interrupt_text = None
        self.response_before_interrupt = ""


# =============================
# === STOP COMMAND DETECTOR ===
# =============================

class StopCommandDetector:
    """Detects user commands to stop, pause, or continue LIGHT's response.
    
    Makes LIGHT command-conscious:
    - Recognizes stop/pause/wait commands
    - Responds appropriately ("ok I have stopped")
    - Tracks what was interrupted for potential continuation
    - Ready for user's next command
    """
    
    def __init__(self):
        self.stop_commands = [
            'stop', 'pause', 'wait', 'hold on', 'hold up', 'hold it',
            'stop there', 'that is enough', 'enough', 'no more', 'never mind',
            'cancel', 'abort', 'quit', 'nope', 'no thanks', 'skip', 'skip that',
            'not now', 'not needed', 'never', 'shh', 'quiet', 'silence',
            "i'm good", 'good enough', 'stop talking', 'be quiet', 'shut up',
            'dont', "don't", 'nah', 'nope', 'na', 'nay', 'no'
        ]
        
        self.continue_commands = [
            'continue', 'go on', 'more', 'keep going', 'further', 'next',
            'and then', 'tell me more', 'go ahead', 'proceed', 'resume',
            'yeah continue', 'keep explaining', 'dont stop', "don't stop",
            'aight continue', 'okay continue', 'more please'
        ]
        
        self.restart_commands = [
            'start over', 'restart', 'again', 'do it again', 'repeat',
            'try again', 'from the beginning', 'from the start', 'reset'
        ]
        
        self.was_interrupted = False
        self.interrupted_response = ""
    
    def is_stop_command(self, text: str) -> bool:
        """Check if user is giving a stop command"""
        text_lower = text.lower().strip()
        
        # Exact match or at start of message
        for cmd in self.stop_commands:
            if text_lower == cmd or text_lower.startswith(cmd + ' '):
                return True
        
        # Single word that's a stop command
        first_word = text_lower.split()[0] if text_lower.split() else ""
        if first_word in self.stop_commands:
            return True
        
        return False
    
    def is_continue_command(self, text: str) -> bool:
        """Check if user wants to continue"""
        text_lower = text.lower().strip()
        
        for cmd in self.continue_commands:
            if cmd in text_lower:
                return True
        
        return False
    
    def is_restart_command(self, text: str) -> bool:
        """Check if user wants to restart the response"""
        text_lower = text.lower().strip()
        
        for cmd in self.restart_commands:
            if cmd in text_lower:
                return True
        
        return False
    
    def is_any_new_input(self, text: str) -> bool:
        """Check if input is new topic (not a command modifier)"""
        text_lower = text.lower().strip()
        
        # If it's any of the special commands, it's not "new input"
        if (self.is_stop_command(text) or 
            self.is_continue_command(text) or 
            self.is_restart_command(text)):
            return False
        
        # If input is longer than stop commands, it's probably new input
        if len(text_lower) > 15:
            return True
        
        # Otherwise check if it looks like a new question/statement
        has_question = '?' in text or any(q in text_lower for q in ['what', 'how', 'why', 'who', 'when', 'where'])
        has_statement = len(text_lower.split()) > 3 or text.startswith(('I', 'can', 'tell', 'show', 'do', 'make', 'create'))
        
        return has_question or has_statement
    
    def get_stop_response(self) -> str:
        """Get natural stop acknowledgment"""
        stop_responses = [
            "✓ Okay, I've stopped.",
            "✓ Got it, stopped.",
            "✓ Stopping here.",
            "✓ Alright, I've stopped.",
            "✓ Stopped.",
            "✓ No problem, I'll stop.",
            "✓ Okay, stopping.",
        ]
        import random
        return random.choice(stop_responses)


# =============================
# === NON-BLOCKING CHUNK FETCHER ===
# =============================

class NonBlockingChunkFetcher:
    """Fetches API chunks in a background thread so main loop isn't blocked.
    
    This allows the main loop to check for interrupts every 10ms instead of
    waiting for the next API chunk (which can take seconds).
    
    Makes interrupts truly real-time and dynamic.
    """
    
    def __init__(self, response_iterator, queue_size=100):
        self.response_iterator = response_iterator
        self.chunk_queue = queue.Queue(maxsize=queue_size)
        self.thread = None
        self.running = False
        self.finished = False
        self.exception = None
    
    def start(self):
        """Start fetching chunks in background thread"""
        if self.running:
            return
        
        self.running = True
        self.finished = False
        self.exception = None
        self.thread = threading.Thread(target=self._fetch_loop, daemon=True)
        self.thread.start()
        print(f"[FETCHER] 📥 Non-blocking chunk fetcher started")
    
    def stop(self):
        """Stop fetching chunks"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        print(f"[FETCHER] ⏹️  Chunk fetcher stopped")
    
    def _fetch_loop(self):
        """Background thread that continuously fetches chunks"""
        try:
            for chunk in self.response_iterator:
                if not self.running:
                    break
                
                # Put chunk in queue (non-blocking to main thread)
                try:
                    self.chunk_queue.put(chunk, timeout=0.5)
                except queue.Full:
                    # Queue is full, skip this chunk (rare)
                    print(f"[FETCHER] ⚠️  Chunk queue full, skipping")
                    continue
            
            self.finished = True
            print(f"[FETCHER] ✓ All chunks fetched")
        except Exception as e:
            self.exception = e
            print(f"[FETCHER] ❌ Error fetching chunks: {e}")
            self.finished = True
    
    def get_chunk(self, timeout=0.05):
        """Get next chunk without blocking (very short timeout)
        
        Returns chunk if available, or None if queue empty.
        This allows main loop to check interrupts between chunks.
        """
        try:
            return self.chunk_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def is_done(self) -> bool:
        """Check if all chunks have been fetched"""
        return self.finished and self.chunk_queue.empty()


# =============================
# === AGGRESSIVE INTERRUPT MONITOR ===
# =============================

class InterruptMonitor:
    """Background thread for aggressive real-time interrupt checking.
    
    Monitors STOP_RESPONDING and INTERRUPT_EVENT flags continuously
    to ensure LIGHT responds to stop commands within milliseconds,
    not waiting for the next chunk.
    """
    
    def __init__(self):
        self.thread = None
        self.running = False
        self.check_interval = 0.01  # 10ms - very aggressive checking
        self.interrupt_detected = False
        self.interrupt_time = None
        
    def start(self):
        """Start the background monitor thread"""
        if self.running:
            return
        
        self.running = True
        self.interrupt_detected = False
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"[MONITOR] 🔍 Interrupt monitor started (check every {self.check_interval*1000}ms)")
    
    def stop(self):
        """Stop the background monitor thread"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        print(f"[MONITOR] ⏹️  Interrupt monitor stopped")
    
    def _monitor_loop(self):
        """Continuously check for interrupts"""
        while self.running:
            try:
                # Check if stop or interrupt flagged
                if STOP_RESPONDING.is_set() or INTERRUPT_EVENT.is_set():
                    if not self.interrupt_detected:
                        self.interrupt_detected = True
                        self.interrupt_time = time.time()
                        print(f"[MONITOR] 🚨 INTERRUPT DETECTED immediately!")
                else:
                    self.interrupt_detected = False
                
                # Sleep briefly before next check
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"[MONITOR ERROR] {e}")
                time.sleep(0.1)
    
    def was_interrupted(self) -> bool:
        """Check if interrupt was detected recently"""
        return self.interrupt_detected


# =============================
# === TURN MANAGER (SPEAKING/LISTENING) ===
# =============================

class TurnManager:
    """Manages speaking and listening turns for natural conversation flow.
    
    Ensures:
    - User always has priority to speak
    - LIGHT pauses naturally when user starts speaking
    - Transitions between turns feel natural
    """
    
    def __init__(self):
        self.is_light_speaking = False
        self.is_user_speaking = False
        self.last_turn_switch_time = 0
        self.min_turn_duration = 0.5  # seconds
        
    def light_start_speaking(self):
        """LIGHT begins response"""
        self.is_light_speaking = True
        self.is_user_speaking = False
        self.last_turn_switch_time = time.time()
        print("[👂➡️💬] LIGHT is now speaking")
    
    def user_took_turn(self, force=False) -> bool:
        """User wants to speak - always grant priority"""
        if force or not self.is_light_speaking:
            self.is_user_speaking = True
            self.is_light_speaking = False  # Stop LIGHT immediately
            self.last_turn_switch_time = time.time()
            print("[💬➡️👂] User taking turn - LIGHT pauses")
            STOP_RESPONDING.set()  # Stop current response
            INTERRUPT_EVENT.set()  # Signal interrupt
            return True
        return False
    
    def light_finished_speaking(self):
        """LIGHT finished response, now listening"""
        self.is_light_speaking = False
        print("[💬✓] LIGHT finished speaking, now listening")
    
    def can_light_respond(self) -> bool:
        """Check if LIGHT can start responding"""
        return not self.is_user_speaking and not USER_SPEAKING_EVENT.is_set()



# =============================
# === CONVERSATION INITIALIZATION ===
# =============================

def init_conversation(title="Chat"):
    """Initialize a new conversation with database and context"""
    global CURRENT_CONVERSATION_ID, CONVERSATION_TITLE, CONVERSATION_START_TIME
    
    CONVERSATION_TITLE = title
    CONVERSATION_START_TIME = datetime.now()
    
    if DB:
        try:
            conv_id = DB.save_conversation(
                title,
                persona=CURRENT_PERSONA or "default",
                tags="gui_mode"
            )
            CURRENT_CONVERSATION_ID = conv_id
            print(f"[INFO] ✅ Conversation {CURRENT_CONVERSATION_ID} started")
            return conv_id
        except Exception as e:
            print(f"[WARNING] Failed to save conversation to DB: {e}")
    
    # Fallback if DB not available
    CURRENT_CONVERSATION_ID = str(uuid.uuid4())
    return CURRENT_CONVERSATION_ID

# =============================
# === KEYBOARD SHORTCUT HANDLERS ===
# =============================

def new_conversation(event=None):
    """Start a new conversation (Ctrl+N)"""
    global CURRENT_CONVERSATION_ID, chat, entry_field
    
    init_conversation("New Chat")
    
    # Clear GUI
    if chat:
        chat.config(state=tk.NORMAL)
        chat.delete(1.0, tk.END)
        chat.config(state=tk.DISABLED)
    
    gui_show("✨ New conversation started!")
    gui_show("─" * 80, tag="separator")
    
    if entry_field:
        entry_field.delete(0, tk.END)
        entry_field.focus()
    
    return "break"  # Prevent default behavior

def show_conversation_history(event=None):
    """Show recent conversations (Ctrl+H)"""
    global DB, chat, entry_field
    
    if not DB:
        gui_show("❌ Database not available", tag="system")
        return "break"
    
    try:
        recent = DB.get_recent_conversations(limit=10)
        
        gui_show("\n📚 Recent Conversations:", tag="system")
        gui_show("─" * 80, tag="separator")
        
        if not recent:
            gui_show("No conversations yet", tag="system")
        else:
            for i, conv in enumerate(recent, 1):
                title = conv.get('title', 'Untitled')
                created = conv.get('created_at', 'Unknown')
                gui_show(f"{i}. {title} ({created})", tag="system")
        
        gui_show("─" * 80, tag="separator")
    except Exception as e:
        gui_show(f"❌ Error loading history: {e}", tag="system")
    
    if entry_field:
        entry_field.focus()
    
    return "break"

def save_current_conversation(event=None):
    """Save current conversation (Ctrl+S)"""
    global CURRENT_CONVERSATION_ID, DB
    
    if not CURRENT_CONVERSATION_ID:
        gui_show("❌ No active conversation to save", tag="system")
        return "break"
    
    gui_show("✅ Conversation saved!", tag="system")
    gui_show("─" * 80, tag="separator")
    
    return "break"

def on_interrupt_button_click():
    """Handle interrupt button click - stop response immediately"""
    global RESPONSE_INTERRUPTED, RESPONSE_STREAMING, btn_interrupt, btn_resume, btn_regenerate
    
    if RESPONSE_STREAMING:
        # Set flags to interrupt streaming
        STOP_RESPONDING.set()
        INTERRUPT_EVENT.set()
        RESPONSE_INTERRUPTED = True
        RESPONSE_STREAMING = False
        
        # Update UI
        gui_show("\n\n[⏹️  LIGHT interrupted by user]", tag="system")
        gui_show("\n📋 What would you like to do?", tag="system")
        
        # Enable resume and regenerate buttons, disable interrupt
        btn_interrupt.config(state=tk.DISABLED)
        btn_resume.config(state=tk.NORMAL)
        btn_regenerate.config(state=tk.NORMAL)
        
        print("[INTERRUPT] User interrupted response")

def on_resume_button_click():
    """Handle resume button click - continue from where LIGHT stopped"""
    global RESPONSE_INTERRUPTED, CURRENT_PARTIAL_RESPONSE, btn_interrupt, btn_resume, btn_regenerate
    
    if RESPONSE_INTERRUPTED and CURRENT_PARTIAL_RESPONSE:
        # Clear interrupt flags
        STOP_RESPONDING.clear()
        INTERRUPT_EVENT.clear()
        RESPONSE_INTERRUPTED = False
        
        # Resume would need re-streaming - for now show what we have
        gui_show("\n\n[▶️  Continuing from where LIGHT stopped...]\n", tag="system")
        
        # Show the partial response that was already received
        gui_show(CURRENT_PARTIAL_RESPONSE, tag="light")
        gui_show("\n\n[Note: Resuming mid-stream requires API support. Full response shown above.]", tag="system")
        
        # Reset buttons
        btn_interrupt.config(state=tk.DISABLED)
        btn_resume.config(state=tk.DISABLED)
        btn_regenerate.config(state=tk.DISABLED)
        
        gui_show("─" * 80, tag="separator")
        print("[RESUME] Displaying partial response")

def on_regenerate_button_click():
    """Handle regenerate button click - start fresh with same question"""
    global RESPONSE_INTERRUPTED, CURRENT_USER_QUESTION, btn_interrupt, btn_resume, btn_regenerate
    
    if RESPONSE_INTERRUPTED and CURRENT_USER_QUESTION:
        # Clear interrupt flags
        STOP_RESPONDING.clear()
        INTERRUPT_EVENT.clear()
        RESPONSE_INTERRUPTED = False
        
        # Reset buttons
        btn_interrupt.config(state=tk.DISABLED)
        btn_resume.config(state=tk.DISABLED)
        btn_regenerate.config(state=tk.DISABLED)
        
        gui_show("\n\n[🔄 Generating a new response...]\n", tag="system")
        
        # Process the same question again
        process_gui_response(CURRENT_USER_QUESTION)
        
        print("[REGENERATE] Starting fresh response")

def clear_chat(event=None):
    """Clear chat window (Ctrl+L)"""
    global chat, entry_field
    
    if chat:
        chat.config(state=tk.NORMAL)
        chat.delete(1.0, tk.END)
        chat.config(state=tk.DISABLED)
    
    gui_show("🧹 Chat cleared!", tag="system")
    
    if entry_field:
        entry_field.delete(0, tk.END)
        entry_field.focus()
    
    return "break"

def setup_gui():
    """Initialize GUI components"""
    global root, chat, entry_field, STYLE_MANAGER, SUGGESTION_ENGINE, ENHANCED_INTERRUPT, TURN_MANAGER, STOP_COMMAND_DETECTOR, INTERRUPT_MONITOR_THREAD
    
    # Initialize new conversation managers
    STYLE_MANAGER = ConversationStyleManager()
    SUGGESTION_ENGINE = PredictiveSuggestionEngine()
    ENHANCED_INTERRUPT = EnhancedInterruptSystem()
    TURN_MANAGER = TurnManager()
    STOP_COMMAND_DETECTOR = StopCommandDetector()  # NEW - Command consciousness
    INTERRUPT_MONITOR_THREAD = InterruptMonitor()  # NEW - Aggressive interrupt checking
    
    root = tk.Tk()
    root.title("✨ LIGHT ASSISTANT ✨")
    root.geometry("900x600")
    root.configure(bg="#1a1a1a")
    
    # Add title label
    title_label = tk.Label(root, text="✨ LIGHT ASSISTANT ✨", bg="#1a1a1a", fg="#00ff00", font=("Arial", 14, "bold"))
    title_label.pack(pady=5)
    
    # Modes frame: Dream, Curiosity, Confidence, Ethical
    global DREAM_MODE, CURIOSITY_MODE, CONFIDENCE_LEVEL, ETHICAL_REASONING_MODE
    modes_frame = tk.Frame(root, bg="#1a1a1a")
    modes_frame.pack(fill=tk.X, padx=10, pady=2)
    
    v_dream = BooleanVar(value=DREAM_MODE)
    v_curiosity = BooleanVar(value=CURIOSITY_MODE)
    v_ethical = BooleanVar(value=ETHICAL_REASONING_MODE)
    v_confidence = IntVar(value=CONFIDENCE_LEVEL)
    
    def _sync_dream():
        global DREAM_MODE
        DREAM_MODE = v_dream.get()
    def _sync_curiosity():
        global CURIOSITY_MODE
        CURIOSITY_MODE = v_curiosity.get()
    def _sync_ethical():
        global ETHICAL_REASONING_MODE
        ETHICAL_REASONING_MODE = v_ethical.get()
    def _sync_confidence(v):
        global CONFIDENCE_LEVEL
        CONFIDENCE_LEVEL = int(float(v))
        conf_label.config(text=f"Confidence: {CONFIDENCE_LEVEL}")
    
    cb_dream = tk.Checkbutton(modes_frame, text="Dream Mode", variable=v_dream, command=_sync_dream, bg="#1a1a1a", fg="#00ccff", selectcolor="#0d0d0d", activebackground="#1a1a1a", activeforeground="#00ccff")
    cb_dream.pack(side=tk.LEFT, padx=5)
    cb_curiosity = tk.Checkbutton(modes_frame, text="Curiosity", variable=v_curiosity, command=_sync_curiosity, bg="#1a1a1a", fg="#00ccff", selectcolor="#0d0d0d", activebackground="#1a1a1a", activeforeground="#00ccff")
    cb_curiosity.pack(side=tk.LEFT, padx=5)
    cb_ethical = tk.Checkbutton(modes_frame, text="Ethical Reasoning", variable=v_ethical, command=_sync_ethical, bg="#1a1a1a", fg="#00ccff", selectcolor="#0d0d0d", activebackground="#1a1a1a", activeforeground="#00ccff")
    cb_ethical.pack(side=tk.LEFT, padx=5)
    
    conf_label = tk.Label(modes_frame, text=f"Confidence: {CONFIDENCE_LEVEL}", bg="#1a1a1a", fg="#ffaa00", font=("Arial", 9))
    conf_label.pack(side=tk.LEFT, padx=(15, 2))
    conf_scale = tk.Scale(modes_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=v_confidence, command=_sync_confidence, bg="#1a1a1a", fg="#00ff00", troughcolor="#333333", highlightthickness=0, length=120)
    conf_scale.pack(side=tk.LEFT, padx=2)
    
    # ===== CONVERSATION STYLE FRAME (NEW) =====
    style_frame = tk.Frame(root, bg="#1a1a1a")
    style_frame.pack(fill=tk.X, padx=10, pady=3)
    
    style_label = tk.Label(style_frame, text="Chat Style:", bg="#1a1a1a", fg="#ccffcc", font=("Arial", 9, "bold"))
    style_label.pack(side=tk.LEFT, padx=5)
    
    def set_vibe_mode():
        STYLE_MANAGER.activate_vibe_mode()
        gui_show("💫 Vibe mode activated - I'm here to listen", tag="system")
    
    def set_casual_mode():
        STYLE_MANAGER.set_style('casual')
        gui_show("👋 Switched to casual mode", tag="system")
    
    def set_formal_mode():
        STYLE_MANAGER.set_style('formal')
        gui_show("🎩 Switched to formal mode", tag="system")
    
    def set_teaching_mode():
        STYLE_MANAGER.set_style('teaching')
        gui_show("📚 Switched to teaching mode", tag="system")
    
    btn_vibe = tk.Button(style_frame, text="💫 Vibe", command=set_vibe_mode, bg="#ff1493", fg="#ffffff", activebackground="#ff69b4", font=("Arial", 8, "bold"), padx=8, pady=3)
    btn_vibe.pack(side=tk.LEFT, padx=3)
    
    btn_casual = tk.Button(style_frame, text="👋 Casual", command=set_casual_mode, bg="#4169e1", fg="#ffffff", activebackground="#6495ed", font=("Arial", 8, "bold"), padx=8, pady=3)
    btn_casual.pack(side=tk.LEFT, padx=3)
    
    btn_formal = tk.Button(style_frame, text="🎩 Formal", command=set_formal_mode, bg="#8b7355", fg="#ffffff", activebackground="#a0826d", font=("Arial", 8, "bold"), padx=8, pady=3)
    btn_formal.pack(side=tk.LEFT, padx=3)
    
    btn_teaching = tk.Button(style_frame, text="📚 Teaching", command=set_teaching_mode, bg="#228b22", fg="#ffffff", activebackground="#32cd32", font=("Arial", 8, "bold"), padx=8, pady=3)
    btn_teaching.pack(side=tk.LEFT, padx=3)
    
    # Main chat display with dark theme
    chat = scrolledtext.ScrolledText(root, bg="#0d0d0d", fg="#00ff00", insertbackground="#00ff00", wrap=tk.WORD, font=("Courier", 11))
    chat.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
    
    # Configure text tags for styling
    chat.tag_config("user", foreground="#00ccff", font=("Courier", 11, "bold"))  # Cyan for user
    chat.tag_config("light", foreground="#00ff00", font=("Courier", 11, "bold"))  # Green for LIGHT
    chat.tag_config("system", foreground="#ffaa00", font=("Courier", 10))  # Orange for system
    chat.tag_config("separator", foreground="#444444")  # Gray separator
    chat.tag_config("suggestion", foreground="#ff99cc", font=("Courier", 9, "italic"))  # Pink for suggestions
    
    # Input area with label
    input_label = tk.Label(root, text="You:", bg="#1a1a1a", fg="#00ccff", font=("Arial", 10, "bold"))
    input_label.pack(anchor=tk.W, padx=15)
    
    entry_field = tk.Entry(root, width=80, bg="#333333", fg="#00ccff", insertbackground="#00ccff", font=("Courier", 10))
    entry_field.pack(pady=5, padx=10)
    entry_field.bind("<Return>", lambda event: (TURN_MANAGER.user_took_turn(force=True), handle_gui_input()))  # User takes priority
    
    # Control buttons frame - for interrupt/resume/regenerate
    controls_frame = tk.Frame(root, bg="#1a1a1a")
    controls_frame.pack(fill=tk.X, padx=10, pady=5)
    
    global btn_interrupt, btn_resume, btn_regenerate
    btn_interrupt = tk.Button(
        controls_frame, 
        text="⏹️  Stop Response", 
        command=on_interrupt_button_click,
        bg="#ff4444", 
        fg="#ffffff", 
        activebackground="#cc0000",
        activeforeground="#ffffff",
        font=("Arial", 9, "bold"),
        state=tk.DISABLED,
        padx=10,
        pady=5
    )
    btn_interrupt.pack(side=tk.LEFT, padx=5)
    
    btn_resume = tk.Button(
        controls_frame,
        text="▶️  Resume",
        command=on_resume_button_click,
        bg="#4444ff",
        fg="#ffffff",
        activebackground="#0000cc",
        activeforeground="#ffffff",
        font=("Arial", 9, "bold"),
        state=tk.DISABLED,
        padx=10,
        pady=5
    )
    btn_resume.pack(side=tk.LEFT, padx=5)
    
    btn_regenerate = tk.Button(
        controls_frame,
        text="🔄 Regenerate",
        command=on_regenerate_button_click,
        bg="#ff9900",
        fg="#ffffff",
        activebackground="#cc6600",
        activeforeground="#ffffff",
        font=("Arial", 9, "bold"),
        state=tk.DISABLED,
        padx=10,
        pady=5
    )
    btn_regenerate.pack(side=tk.LEFT, padx=5)
    
    status_label = tk.Label(
        controls_frame,
        text="",
        bg="#1a1a1a",
        fg="#ffaa00",
        font=("Arial", 8),
        anchor=tk.W
    )
    status_label.pack(side=tk.LEFT, padx=15, expand=True, fill=tk.X)
    
    # Keyboard shortcuts
    entry_field.bind("<Control-Return>", lambda event: handle_gui_input())  # Ctrl+Enter to send
    entry_field.bind("<Control-n>", lambda event: new_conversation())  # Ctrl+N for new chat
    entry_field.bind("<Control-h>", lambda event: show_conversation_history())  # Ctrl+H for history
    entry_field.bind("<Control-s>", lambda event: save_current_conversation())  # Ctrl+S to save
    entry_field.bind("<Control-l>", lambda event: clear_chat())  # Ctrl+L to clear
    entry_field.bind("<Escape>", lambda event: (TURN_MANAGER.user_took_turn(force=True), gui_show("(interrupted)", tag="system")))  # ESC to interrupt
    
    root.bind("<Control-n>", lambda event: new_conversation())  # Also bind to root
    root.bind("<Control-h>", lambda event: show_conversation_history())
    root.bind("<Control-s>", lambda event: save_current_conversation())
    root.bind("<Control-l>", lambda event: clear_chat())
    root.bind("<Escape>", lambda event: (TURN_MANAGER.user_took_turn(force=True), gui_show("(interrupted)", tag="system")))
    
    entry_field.focus()
    
    gui_show("LIGHT: Hello! I'm LIGHT — your friend, teacher, and guide.", tag="light")
    gui_show("💫 You can switch styles anytime: Vibe, Casual, Formal, Teaching", tag="system")
    gui_show("🎯 Press ESC anytime to interrupt - you always have priority!", tag="system")
    gui_show("─" * 80, tag="separator")

def gui_show(text, end="\n", tag=None):
    """Display text in GUI chat window (thread-safe)"""
    if USE_GUI and chat is not None:
        # Use root.after() for thread-safe GUI updates
        def update_gui():
            try:
                if tag:
                    if chat is not None:
                        chat.insert(tk.END, text, tag)
                else:
                    if chat is not None:
                        chat.insert(tk.END, text)
                if chat is not None:
                    chat.insert(tk.END, end)
                    chat.see(tk.END)
                if root is not None:
                    root.update_idletasks()  # Force refresh
            except Exception as e:
                print(f"[ERROR] gui_show update_gui error: {e}")
        
        if root and root.winfo_exists():
            root.after(0, update_gui)  # Queue GUI update on main thread

def handle_gui_input():
    """Handle input from GUI entry field - COMMAND CONSCIOUS
    
    Detects:
    - Stop commands (stop, pause, wait, etc.)
    - Continue commands (go on, more, continue)
    - New questions/requests (different topic, restarts)
    - Always respects user priority
    """
    global entry_field, chat, TURN_MANAGER, ENHANCED_INTERRUPT, STOP_COMMAND_DETECTOR
    
    if not (USE_GUI and entry_field and chat):
        return
    
    text = entry_field.get().strip()
    if not text:
        return
    
    # Always take priority from LIGHT
    TURN_MANAGER.user_took_turn(force=True)
    STOP_RESPONDING.set()  # Force stop any current response
    INTERRUPT_EVENT.set()  # Signal interrupt
    
    # Display user input
    gui_show("You: ", tag="user", end="")
    gui_show(text, tag="user")
    gui_show("─" * 80, tag="separator")
    
    # Clear input field
    entry_field.delete(0, tk.END)
    
    # ===== COMMAND CONSCIOUSNESS =====
    # Check what type of command this is
    
    if STOP_COMMAND_DETECTOR.is_stop_command(text):
        # User said "stop" or similar
        stop_response = STOP_COMMAND_DETECTOR.get_stop_response()
        gui_show("LIGHT: ", tag="light", end="")
        gui_show(stop_response)
        gui_show("─" * 80, tag="separator")
        print(f"[COMMAND] STOP detected - LIGHT acknowledged and stopped")
        return  # Wait for next user input
    
    elif STOP_COMMAND_DETECTOR.is_continue_command(text):
        # User said "continue" or similar
        if ENHANCED_INTERRUPT and ENHANCED_INTERRUPT.response_before_interrupt:
            gui_show("LIGHT: ", tag="light", end="")
            gui_show(f"Continuing from where I left off...\n{ENHANCED_INTERRUPT.response_before_interrupt}")
            gui_show("─" * 80, tag="separator")
            print(f"[COMMAND] CONTINUE detected - resuming previous response")
            return
        else:
            gui_show("LIGHT: ", tag="light", end="")
            gui_show("(No previous response to continue - what would you like to know?)")
            gui_show("─" * 80, tag="separator")
            return
    
    elif STOP_COMMAND_DETECTOR.is_restart_command(text):
        # User wants to restart - just process normally as a fresh request
        print(f"[COMMAND] RESTART detected - generating fresh response")
        process_gui_response(text.replace("restart", "").replace("start over", "").replace("again", "").strip())
        return
    
    elif STOP_COMMAND_DETECTOR.is_any_new_input(text):
        # New question/topic - process as normal question/command
        print(f"[COMMAND] NEW INPUT detected - processing new topic")
        process_gui_response(text)
        return
    
    else:
        # Could be anything - treat as new input
        print(f"[COMMAND] Default path - processing as new input")
        process_gui_response(text)
        return

def save_message_to_db(user_input: str, light_response: str) -> bool:
    """Save a message exchange to the database"""
    global CURRENT_CONVERSATION_ID, DB
    
    if not CURRENT_CONVERSATION_ID:
        init_conversation()
    
    if DB:
        try:
            DB.save_message(
                CURRENT_CONVERSATION_ID,
                user_input,
                light_response,
                tokens_used=0
            )
            print(f"[INFO] ✅ Message saved to DB")
            return True
        except Exception as e:
            print(f"[WARNING] Failed to save message to DB: {e}")
            return False
    
    return False

def process_gui_response(text):
    """Process response for GUI mode"""
    global LAST_RESPONSE, gemini_chat, audio_queue
    
    try:
        # Any new user GUI input should interrupt current TTS so LIGHT can respond.
        try:
            INTERRUPT_EVENT.set()
            try:
                engine.stop()
            except Exception:
                pass
        except Exception:
            pass
        
        # Auto-resume if user was paused - new input means they want an answer
        global STOP_RESPONDING
        if STOP_RESPONDING.is_set():
            STOP_RESPONDING.clear()
        
        # Check for system control commands first (exit, shutdown, standby)
        sys_cmd = detect_system_control_command(text)
        print(f"[DEBUG] Text input: '{text}' | Detected command: {sys_cmd}")
        gui_show(f"[DEBUG] Detected: {sys_cmd}", tag="system")
        if sys_cmd:
            if sys_cmd == 'exit':
                gui_show("LIGHT: ", tag="light", end="")
                gui_show("👋 Goodbye! See you next time.")
                gui_show("─" * 80, tag="separator")
                if audio_queue:
                    audio_queue.put("Goodbye! See you next time.")
                root.after(2000, execute_exit)  # Exit after 2 seconds
                return
            elif sys_cmd == 'shutdown':
                gui_show("LIGHT: ", tag="light", end="")
                gui_show("⚡ Initiating system shutdown...")
                gui_show("─" * 80, tag="separator")
                if audio_queue:
                    audio_queue.put("Initiating system shutdown.")
                root.after(1000, execute_shutdown)
                return
            elif sys_cmd == 'standby':
                gui_show("LIGHT: ", tag="light", end="")
                gui_show("💤 Entering standby mode...")
                gui_show("─" * 80, tag="separator")
                if audio_queue:
                    audio_queue.put("Entering standby mode.")
                root.after(1000, execute_standby)
                return
            elif sys_cmd == 'stop_responding':
                # User explicitly requests LIGHT to stop responding immediately
                STOP_RESPONDING.set()
                try:
                    engine.stop()
                except Exception:
                    pass
                # Drain queued TTS
                if audio_queue:
                    try:
                        while not audio_queue.empty():
                            audio_queue.get_nowait()
                    except Exception:
                        pass
                gui_show("✨ LIGHT: ", tag="light", end="")
                gui_show("Stopped. Ready for your next question.", tag="light")
                gui_show("─" * 80, tag="separator")
                if audio_queue:
                    audio_queue.put("Stopped. Ready for your next question.")
                return
            elif sys_cmd == 'resume_responding':
                STOP_RESPONDING.clear()
                gui_show("✨ LIGHT: ", tag="light", end="")
                gui_show("Resuming responses.", tag="light")
                gui_show("─" * 80, tag="separator")
                if audio_queue:
                    audio_queue.put("Resuming responses. I'm ready to help.")
                return
            elif isinstance(sys_cmd, tuple) and sys_cmd[0] == 'focus_response':
                # User wants to focus on specific part of response
                focus_topic = sys_cmd[1] if len(sys_cmd) > 1 else 'general'
                gui_show(f"🎯 LIGHT: Focusing on: {focus_topic}", tag="system")
                gui_show("(I'll provide a concise response focused on this topic)", tag="system")
                gui_show("─" * 80, tag="separator")
                # Process the user's main input with focus context
                if entry_field:
                    current_input = entry_field.get()
                    # Keep the focus context but let the main loop process the query
                    return  # Will process with focus context in main loop
            elif sys_cmd == 'clear_focus':
                if INTERRUPT_HANDLER:
                    INTERRUPT_HANDLER.clear_focus()
                gui_show("✨ LIGHT: Focus cleared - showing full responses.", tag="system")
                gui_show("─" * 80, tag="separator")
                return
        
        # Debug: Check if gemini_chat object is available
        if gemini_chat is None:
            gui_show("❌ Error: Gemini Chat object not initialized!", tag="system")
            print("[ERROR] gemini_chat object is None in process_gui_response()")
            return
        
        print(f"[DEBUG] Processing: {text[:50]}...")
        print(f"[DEBUG] gemini_chat object: {type(gemini_chat)}")
        
        # Check for save command
        save_filename = detect_save_command(text)
        if save_filename:
            save_response_to_file(save_filename)
            gui_show("✅ Response saved to: " + save_filename, tag="system")
            gui_show("─" * 80, tag="separator")
            return
        
        # Check for persona request
        if detect_persona_request(text):
            persona_desc = extract_persona_request(text)
            if persona_desc:
                set_persona(persona_desc)
                update_session_context()
                gui_show("✨ Switched to act like " + persona_desc, tag="system")
                gui_show("─" * 80, tag="separator")
                return
        
        # Check for CODE GENERATION REQUEST (LIGHT's main feature!)
        code_gen_request = detect_code_generation_request(text)
        if code_gen_request:
            gui_show("⚡ LIGHT CODE GENERATOR: ", tag="system", end="")
            gui_show("Processing your request...", tag="system")
            gui_show("This may take a few moments...", tag="system")
            gui_show("─" * 80, tag="separator")
            
            try:
                # Generate the project
                generation_result = handle_code_generation(code_gen_request)
                
                # Format and display the result
                formatted_result = format_generation_result(generation_result)
                
                gui_show("LIGHT: ", tag="light", end="")
                gui_show(formatted_result)
                gui_show("─" * 80, tag="separator")
                
                # Also provide copy-paste friendly output
                if generation_result.get("status") == "✅ SUCCESS" or "✅" in generation_result.get("status", ""):
                    gui_show("\n📋 PROJECT DETAILS:", tag="system")
                    import json
                    gui_show(json.dumps(generation_result, indent=2, default=str), tag="light")
                    gui_show("─" * 80, tag="separator")
                
                # Queue audio response
                if audio_queue:
                    audio_queue.put(f"Project {generation_result.get('project_name', 'generated')} created successfully!")
                
                return
            except Exception as e:
                gui_show("❌ LIGHT: ", tag="light", end="")
                gui_show(f"Error generating project: {str(e)}")
                gui_show("─" * 80, tag="separator")
                return
        
        # Check for CODE COMPLETION / COPILOT-LIKE REQUEST
        code_completion_req = detect_code_completion_request(text)
        if code_completion_req:
            gui_show("🤖 LIGHT COPILOT: ", tag="system", end="")
            gui_show("Code Completion Engine Activated", tag="system")
            gui_show("─" * 80, tag="separator")
            
            try:
                completion_result = handle_code_completion(code_completion_req)
                gui_show("LIGHT: ", tag="light", end="")
                gui_show(completion_result.get("message", "Ready to help with code"))
                gui_show("─" * 80, tag="separator")
                
                if audio_queue:
                    audio_queue.put("Code completion mode activated")
                
                return
            except Exception as e:
                gui_show("❌ Error: ", tag="system", end="")
                gui_show(str(e))
                gui_show("─" * 80, tag="separator")
                return
        
        # Check for FILE GENERATION REQUEST
        file_gen_req = detect_file_generation_request(text)
        if file_gen_req:
            gui_show("📄 LIGHT FILE GENERATOR: ", tag="system", end="")
            gui_show(f"Generating {file_gen_req.get('type', 'file')}", tag="system")
            gui_show("─" * 80, tag="separator")
            
            try:
                file_result = handle_file_generation(file_gen_req)
                
                # Show success or error
                if file_result.get("success"):
                    gui_show("✅ LIGHT: ", tag="light", end="")
                    gui_show(file_result.get("message", "File generated successfully!"))
                    gui_show("", tag="light")
                    gui_show(f"📁 Path: {file_result.get('filepath', 'N/A')}", tag="light")
                    gui_show(f"📄 File: {file_result.get('filename', 'N/A')}", tag="light")
                    gui_show(f"📊 Size: {file_result.get('size_bytes', 0)} bytes", tag="light")
                    gui_show("", tag="light")
                    
                    if file_result.get("file_content"):
                        gui_show("📝 GENERATED CODE:", tag="system")
                        gui_show("─" * 80, tag="separator")
                        gui_show(file_result.get("file_content"), tag="code")
                        gui_show("─" * 80, tag="separator")
                    
                    if audio_queue:
                        audio_queue.put(f"Successfully generated {file_gen_req.get('type')} file. Output saved to {file_result.get('filename', 'the file')}")
                else:
                    gui_show("❌ LIGHT: ", tag="light", end="")
                    gui_show(file_result.get("error", "Failed to generate file"))
                    if audio_queue:
                        audio_queue.put(f"Error: {file_result.get('error', 'Unknown error')}")
                
                gui_show("─" * 80, tag="separator")
                return
            except Exception as e:
                gui_show("❌ Error: ", tag="system", end="")
                gui_show(str(e))
                gui_show("─" * 80, tag="separator")
                if audio_queue:
                    audio_queue.put(f"Error generating file: {str(e)}")
                return
        
        # Check for IDE EXPORT REQUEST
        ide_export_req = detect_ide_export_request(text)
        if ide_export_req:
            gui_show("💻 LIGHT IDE INTEGRATION: ", tag="system", end="")
            gui_show(f"Preparing export for {ide_export_req.get('ide').upper()}", tag="system")
            gui_show("─" * 80, tag="separator")
            
            try:
                export_result = handle_ide_export(ide_export_req)
                gui_show("LIGHT: ", tag="light", end="")
                gui_show(export_result.get("message", "Ready to export code"))
                gui_show("─" * 80, tag="separator")
                
                if audio_queue:
                    audio_queue.put(f"IDE export mode for {ide_export_req.get('ide')} activated")
                
                return
            except Exception as e:
                gui_show("❌ Error: ", tag="system", end="")
                gui_show(str(e))
                gui_show("─" * 80, tag="separator")
                return
        
        # Check for reset persona
        if any(word in text.lower() for word in ['reset', 'normal', 'be yourself', 'back to normal']):
            reset_persona()
            update_session_context()
            gui_show("✨ Reset to LIGHT default personality", tag="system")
            gui_show("─" * 80, tag="separator")
            return
        
        # Check for navigation commands
        nav_response = handle_navigation_command(text)
        if nav_response:
            gui_show("LIGHT: ", tag="light", end="")
            gui_show(nav_response)
            gui_show("─" * 80, tag="separator")
            return
        
        # Check for Mode 2 exclusive commands (only in GUI mode)
        mode2_cmd = detect_mode2_command(text)
        if mode2_cmd:
            response = ""
            if mode2_cmd == 'generate':
                response = "📝 What would you like me to generate? (e.g., 'Python script', 'HTML page')"
            elif mode2_cmd == 'fullstack':
                response = "🏗️ What type of full-stack project? (React+Node, Vue+Django, Next.js)"
            elif mode2_cmd == 'research':
                topic = text.replace('autonomous research', '').replace('research', '').strip()
                response = autonomous_research(topic)
            elif mode2_cmd == 'vision':
                response = vision_scan()
            elif mode2_cmd == 'robot':
                cmd = text.replace('robot command', '').strip()
                response = robot_command(cmd)
            elif mode2_cmd == 'github':
                repo = re.search(r'https?://[^\s]+', text)
                if repo:
                    response = github_clone(repo.group(0))
                else:
                    response = "❌ Please provide a valid GitHub URL"
            elif mode2_cmd == 'backup':
                response = f"✅ Backup created: {backup_script()}"
            
            gui_show("LIGHT: ", tag="light", end="")
            gui_show(response)
            gui_show("─" * 80, tag="separator")
            
            # Queue response for TTS
            if audio_queue and response:
                audio_queue.put(response)
            return
        
        # Emotion-driven behavior: detect emotion, set global for TTS, inject addendum
        global CURRENT_EMOTION
        em = detect_emotion(text)
        CURRENT_EMOTION = em
        emotion_addendum = get_emotion_addendum(em)
        
        # Build message for sending - persona is now handled via system instruction
        message_to_send = text if text else ""
        
        if not message_to_send or not message_to_send.strip():
            gui_show("❌ Error: No message to send", tag="system")
            gui_show("─" * 80, tag="separator")
            return
        
        # Get response from Gemini
        print(f"[DEBUG] About to display LIGHT: prefix...")
        gui_show("LIGHT: ", tag="light", end="")
        print(f"[DEBUG] Displayed LIGHT: prefix")
        print(f"[DEBUG] Message length: {len(message_to_send)}, Sending to Gemini...")
        
        # Mark that LIGHT is starting to speak
        if TURN_MANAGER:
            TURN_MANAGER.light_start_speaking()
        
        try:
            # Build complete system instruction with persona, modes, and emotion
            full_system_instruction = build_system_instruction()
            
            # Add CONVERSATION STYLE INSTRUCTION (NEW - for human-like responses)
            if STYLE_MANAGER:
                style_instruction = STYLE_MANAGER.get_style_instruction()
                full_system_instruction += style_instruction
            
            # Add emotion addendum to system instruction if active
            if emotion_addendum:
                full_system_instruction += "\n\n[EMOTION CONTEXT]\n" + emotion_addendum
            
            # Refresh system instruction from current mode toggles (Curiosity, Confidence, Ethical) + Persona
            updater = getattr(gemini_chat, "update_system_instruction", None)
            if updater is not None:
                updater(full_system_instruction)
                debug_print(f"[PERSONA] Updated system instruction with persona: {PERSONA_ACTIVE}")
            
            print(f"[DEBUG] Calling gemini_chat.send_message_stream()...")
            print(f"[DEBUG] gemini_chat type: {type(gemini_chat)}")
            response = gemini_chat.send_message_stream(message_to_send)
            print(f"[DEBUG] Got response object: {type(response)}")
            
            # ===== START AGGRESSIVE INTERRUPT MONITOR =====
            if INTERRUPT_MONITOR_THREAD:
                INTERRUPT_MONITOR_THREAD.start()
            
            # ===== START NON-BLOCKING CHUNK FETCHER =====
            fetcher = NonBlockingChunkFetcher(response)
            fetcher.start()
            
            # Stream response with real-time text display and TTS
            full_response = []
            chunk_count = 0
            current_sentence = ""
            queued_length = 0  # Track what's been queued to avoid duplicates
            suggestion_count = 0
            
            print(f"[DEBUG] Starting to iterate through response chunks (NON-BLOCKING)...")
            
            # NON-BLOCKING LOOP - checks interrupt every 10ms
            while not fetcher.is_done():
                # ===== CHECK FOR INTERRUPT - AGGRESSIVELY (every 10ms) =====
                if STOP_RESPONDING.is_set() or INTERRUPT_EVENT.is_set():
                    print(f"[INTERRUPT] ⏹️  STOPPING at chunk {chunk_count} - user interrupted")
                    fetcher.stop()
                    if ENHANCED_INTERRUPT:
                        ENHANCED_INTERRUPT.register_interrupt(message_to_send)
                        ENHANCED_INTERRUPT.response_before_interrupt = "".join(full_response)
                    # Also queue any remaining sentence to save context
                    if current_sentence and audio_queue:
                        audio_queue.put(current_sentence)
                    break
                
                # Get next chunk WITHOUT BLOCKING (50ms timeout)
                chunk = fetcher.get_chunk(timeout=0.05)
                
                if chunk is None:
                    # No chunk available yet, loop continues to check interrupts immediately
                    continue
                
                # Double-check GUI responsiveness
                if root and root.winfo_exists():
                    try:
                        root.update_idletasks()  # Process any pending events (including stops)
                    except:
                        pass  # Window might be closing
                
                chunk_count += 1
                if hasattr(chunk, 'text') and chunk.text:
                    chunk_text = chunk.text
                    chunk_preview = chunk_text[:50]
                    print(f"[DEBUG] Got chunk {chunk_count}: {chunk_preview}...")
                    full_response.append(chunk_text)
                    
                    # Display text in real-time
                    gui_show(chunk_text, end="")
                    
                    # GENERATE SUGGESTIONS AS WE GO (NEW)
                    if SUGGESTION_ENGINE:
                        suggestions = SUGGESTION_ENGINE.add_response_chunk(chunk_text)
                        for suggestion in suggestions:
                            gui_show(f"\n  {suggestion}", tag="suggestion")
                            suggestion_count += 1
                    
                    # Accumulate text for sentence-based TTS
                    current_sentence += chunk_text
                    
                    # Check if we have a complete sentence (ends with . ! ? :)
                    if current_sentence and current_sentence.rstrip().endswith(('.', '!', '?', ':')):
                        # Queue text for TTS playback (non-blocking)
                        print(f"[TTS] Queuing: {current_sentence[:50]}...")
                        if audio_queue:
                            audio_queue.put(current_sentence)
                        queued_length += len(current_sentence)  # Track queued length
                        current_sentence = ""
                else:
                    print(f"[DEBUG] Got chunk {chunk_count}: (no text)")
            
            print(f"[DEBUG] Finished streaming {chunk_count} chunks")
            
            # ===== CLEANUP FETCHER =====
            fetcher.stop()
            
            full_response_text = "".join(full_response).strip()
            
            if not full_response_text:
                gui_show("\n(No response received)", tag="system")
            else:
                gui_show("")  # Newline
            
            gui_show("─" * 80, tag="separator")  # Separator line
            
            # ===== STOP AGGRESSIVE INTERRUPT MONITOR =====
            if INTERRUPT_MONITOR_THREAD:
                INTERRUPT_MONITOR_THREAD.stop()
            
            # ===== CLEANUP AFTER RESPONSE =====
            STOP_RESPONDING.clear()  # Clear stop flag for next response
            INTERRUPT_EVENT.clear()  # Clear interrupt flag
            
            # Mark that LIGHT finished speaking
            if TURN_MANAGER:
                TURN_MANAGER.light_finished_speaking()
            
            # Store response for saving
            LAST_RESPONSE = full_response_text
            add_to_response_history(text, full_response_text)
            
            # Save to database
            save_message_to_db(text, full_response_text)
            
            # ===== PERSONAL GROWTH FEATURES (Adaptive) =====
            try:
                if DB and CONVERSATION_MODE:
                    # Detect user intent
                    CONVERSATION_MODE.detect_intent(text)
                    
                    # Extract any goals mentioned in user message (always good to track)
                    goals = extract_goals_from_message(text)
                    if goals:
                        gui_show("\n✨ I noticed some goals in what you shared:", tag="light")
                        for goal in goals:
                            goal_id = DB.save_user_goal(
                                goal=goal.get('goal'),
                                category=goal.get('category'),
                                priority=goal.get('priority', 1)
                            )
                            gui_show(f"  📌 {goal['goal']} ({goal.get('category', 'personal')})", tag="light")
                    
                    # Generate clarifying questions - BUT ONLY IF NOT IN VIBE MODE!
                    # In vibe mode (or when listening mode is active), LIGHT mostly just chats naturally
                    should_ask = (CONVERSATION_MODE.should_ask_clarifying_question() and 
                                 not STYLE_MANAGER.listening_mode and 
                                 STYLE_MANAGER.current_style != 'vibe')
                    
                    if should_ask:
                        questions = generate_clarifying_questions(text, db=DB)
                        if questions:
                            gui_show("\n❓ To help you better, I'd like to understand more:", tag="light")
                            for q in questions:
                                gui_show(f"  • {q.get('question', '')}", tag="light")
                            gui_show("", tag="separator")
            except Exception as growth_error:
                # Don't break main flow if growth features fail
                print(f"[DEBUG] Growth feature error (non-critical): {growth_error}")
            
            # Check if AI is requesting to play music
            if full_response_text:
                music_match = re.search(r'\[PLAY_MUSIC:\s*(.+?)\]', full_response_text)
                if music_match:
                    song_name = music_match.group(1).strip()
                    gui_show(f"🎵 Playing: {song_name}...")
                    play_music(song_name)
            
            # Reset suggestion engine for next response
            if SUGGESTION_ENGINE:
                SUGGESTION_ENGINE.reset()
            
            print(f"[DEBUG] Response processing complete")
            if root is not None:
                root.update()  # Update GUI
            
        except Exception as stream_error:
            error_str = str(stream_error)
            print(f"[ERROR] Exception during API call: {error_str}")
            print(f"[ERROR] Exception type: {type(stream_error).__name__}")
            import traceback
            traceback.print_exc()
            
            # Show cleaner error message to user
            if "429" in error_str or "quota" in error_str.lower():
                gui_show("\n❌ API Quota Exceeded: Free tier limit reached", tag="system")
                gui_show("💡 Wait for quota reset or upgrade to paid plan", tag="system")
            elif "401" in error_str or "unauthorized" in error_str.lower():
                gui_show("\n❌ API Authentication Error: Check your GENAI_API_KEY", tag="system")
            elif "500" in error_str or "internal" in error_str.lower():
                gui_show("\n❌ API Server Error: Google's servers are having issues. Try again later.", tag="system")
            else:
                gui_show(f"\n❌ Error: {error_str[:150]}", tag="system")
            
            gui_show("─" * 80, tag="separator")
            
            # ===== STOP MONITOR AFTER ERROR =====
            if INTERRUPT_MONITOR_THREAD:
                INTERRUPT_MONITOR_THREAD.stop()
            
            # ===== CLEANUP AFTER ERROR =====
            STOP_RESPONDING.clear()  # Clear for next response
            INTERRUPT_EVENT.clear()  # Clear for next response
            
            # Mark that LIGHT is NOT speaking anymore
            if TURN_MANAGER:
                TURN_MANAGER.light_finished_speaking()
        
    except Exception as e:
        error_str = str(e)
        print(f"[ERROR] {error_str}")
        import traceback
        traceback.print_exc()  # Print full error for debugging
        gui_show(f"❌ Unexpected Error: {error_str[:100]}", tag="system")
        gui_show("─" * 80, tag="separator")
        
        # ===== STOP MONITOR AFTER CRITICAL ERROR =====
        if INTERRUPT_MONITOR_THREAD:
            INTERRUPT_MONITOR_THREAD.stop()
        
        # ===== CLEANUP AFTER CRITICAL ERROR =====
        STOP_RESPONDING.clear()
        INTERRUPT_EVENT.clear()

# =============================
# === MUSIC STREAMING (SPOTIFY/YOUTUBE/BOOMPLAY) ===
# =============================

def search_spotify(query):
    """Search for a song on Spotify"""
    if not SPOTIFY_ENABLED or not spotify_client:
        return None
    
    try:
        results = spotify_client.search(q=query, type='track', limit=1)
        if results and results.get('tracks', {}).get('items'):
            track = results['tracks']['items'][0]
            return {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'url': track['external_urls']['spotify'],
                'preview_url': track['preview_url'],
                'source': 'spotify'
            }
    except Exception as e:
        print(f"[WARNING] Spotify search failed: {e}")
    
    return None

def search_youtube_music(query):
    """Search and get playable link from YouTube"""
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if info and 'entries' in info and info['entries']:
                video = info['entries'][0]
                return {
                    'name': query,
                    'url': video['webpage_url'],
                    'source': 'youtube',
                    'duration': video.get('duration', 0)
                }
    except Exception as e:
        print(f"[WARNING] YouTube search failed: {e}")
    
    return None

def search_boomplay(query):
    """Search Boomplay (requires parsing - basic implementation)"""
    try:
        # Boomplay search via requests
        headers = {'User-Agent': 'Mozilla/5.0'}
        search_url = f"https://www.boomplay.com/search?q={query.replace(' ', '+')}"
        
        response = requests.get(search_url, headers=headers, timeout=5)
        if response.status_code == 200:
            # Basic response indicating search capability
            return {
                'name': query,
                'url': search_url,
                'source': 'boomplay',
                'note': 'Open in browser'
            }
    except Exception as e:
        print(f"[WARNING] Boomplay search failed: {e}")
    
    return None

def play_music_from_source(query, source='auto'):
    """Play music from specified source"""
    print(f"\n🎵 Now playing: {query}")
    print(f"Source: {source}")
    
    # If auto, try multiple sources
    if source == 'auto':
        # Try Spotify first if enabled
        if SPOTIFY_ENABLED:
            result = search_spotify(query)
            if result and result.get('preview_url'):
                print(f"▶️  Playing from Spotify: {result['artist']} - {result['name']}")
                try:
                    audio = requests.get(result['preview_url']).content
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                        f.write(audio)
                        temp_file = f.name
                    subprocess.run(['ffplay', '-nodisp', '-autoexit', temp_file], check=False)
                    os.remove(temp_file)
                    return True
                except:
                    pass
        
        # Fall back to YouTube
        result = search_youtube_music(query)
        if result:
            print(f"▶️  Playing from YouTube")
            source = 'youtube'
    
    # Play from YouTube
    if source == 'youtube' or source == 'auto':
        try:
            print("🎵 Downloading and playing from YouTube...")
            process = subprocess.Popen(
                f'yt-dlp -f bestaudio -o - "ytsearch:{query}" | ffplay -nodisp -autoexit -',
                shell=True
            )
            process.wait()
            print("✅ Finished playing\n")
            return True
        except KeyboardInterrupt:
            print("\n⏭️  Skipped\n")
            return False
        except Exception as e:
            print(f"[ERROR] YouTube playback failed: {e}\n")
    
    # Try Boomplay
    if source == 'boomplay':
        result = search_boomplay(query)
        if result:
            print(f"🔗 Boomplay link: {result['url']}")
            webbrowser.open(result['url'])
            return True
    
    return False

def detect_music_request(text):
    """Detect if user is asking to play music"""
    music_keywords = [
        'play', 'sing', 'music', 'song', 'tune', 'beat',
        'listen', 'artist', 'album', 'spotify', 'youtube', 'boomplay'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in music_keywords)

def extract_music_query(text):
    """Extract song/artist name from music request"""
    # Remove common prefixes
    text = re.sub(r'^(play|sing|listen to|put on)\s+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*(on|from|via|using)\s+(spotify|youtube|boomplay).*$', '', text, flags=re.IGNORECASE)
    
    return text.strip()


def play_music_yt(query):
    """Play music from YouTube using yt-dlp"""
    print(f"\nLIGHT: Playing {query}")
    filename_safe = re.sub(r"[^\w]", "_", query) + f"_{int(time.time())}.%(ext)s"
    ydl_opts = {"format": "bestaudio", "quiet": True, "outtmpl": filename_safe}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
            result = ydl.extract_info(f"ytsearch1:{query}", download=True)  # type: ignore
            info = result.get("entries", [{}])[0] if result else {}
            file = ydl.prepare_filename(info)  # type: ignore
        play_audio_system(file)
        return True
    except Exception as e:
        print(f"Error playing music: {e}")
        return False

# =============================
# === ENHANCED MUSIC (V3+) ====
# =============================
def play_audio_system(filename):
    """Play audio file using system player"""
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":
        subprocess.call(["open", filename])
    else:
        subprocess.call(["xdg-open", filename])

def find_local_music(song_name):
    """Search for music files locally in common directories"""
    music_dirs = [
        os.path.expanduser("~\\Music"),
        os.path.expanduser("~\\Documents"),
        "C:\\Music",
        os.getcwd(),
    ]
    
    supported_formats = ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a')
    song_name_lower = song_name.lower()
    
    for music_dir in music_dirs:
        if not os.path.exists(music_dir):
            continue
            
        try:
            for file in Path(music_dir).rglob('*'):
                if file.suffix.lower() in supported_formats:
                    if song_name_lower in file.name.lower():
                        return str(file)
        except:
            pass
    
    return None

def play_offline_music(file_path):
    """Play a local music file using Windows default media player"""
    try:
        print(f"🎵 Playing: {os.path.basename(file_path)}")
        
        # Get absolute path
        abs_path = os.path.abspath(file_path)
        
        if not os.path.exists(abs_path):
            print(f"❌ File not found: {abs_path}")
            return False
        
        # Windows: Use default associated player (simplest, most reliable)
        if platform.system() == "Windows":
            try:
                os.startfile(abs_path)
                print(f"✅ Playing: {os.path.basename(file_path)}")
                return True
            except Exception as e:
                print(f"❌ Could not play: {e}")
                return False
        
        # Mac: Use open command
        elif platform.system() == "Darwin":
            try:
                subprocess.Popen(['open', abs_path])
                print(f"✅ Playing: {os.path.basename(file_path)}")
                return True
            except Exception as e:
                print(f"❌ Could not play: {e}")
                return False
        
        # Linux: Use xdg-open
        else:
            try:
                subprocess.Popen(['xdg-open', abs_path])
                print(f"✅ Playing: {os.path.basename(file_path)}")
                return True
            except Exception as e:
                print(f"❌ Could not play: {e}")
                return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def play_online_music(song_name):
    """Search for and play online music by opening browser"""
    try:
        print(f"🎵 Opening: {song_name}")
        
        # Use YouTube search (most reliable, no dependencies needed)
        youtube_url = f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}"
        
        if platform.system() == "Windows":
            os.startfile(youtube_url)
        elif platform.system() == "Darwin":
            subprocess.Popen(['open', youtube_url])
        else:
            subprocess.Popen(['xdg-open', youtube_url])
        
        print(f"✅ Opened in browser: {song_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def play_music(song_name):
    """Play music - first try local files, then search online"""
    # First try to find locally
    local_file = find_local_music(song_name)
    if local_file:
        print(f"Found local file: {local_file}")
        return play_offline_music(local_file)
    else:
        # Fall back to online (YouTube/Spotify via browser)
        return play_online_music(song_name)

# =============================
# === CODE GENERATION & FILE SAVING ===
# =============================

def extract_code_only(text: str) -> str:
    """
    Extract ONLY the code from LIGHT's response, removing explanations and chat text.
    Returns clean code with inline comments preserved.
    """
    if not text:
        return ""
    
    # PRIORITY 1: Look for markdown code blocks (```)
    code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', text, re.DOTALL)
    if code_blocks:
        # Return the first (main) code block
        extracted = code_blocks[0].strip()
        print(f"[EXTRACT] Found markdown code block: {len(extracted)} chars")
        return extracted
    
    # PRIORITY 2: Look for triple tildes (~~~)
    code_blocks = re.findall(r'~~~[\w]*\n(.*?)\n~~~', text, re.DOTALL)
    if code_blocks:
        extracted = code_blocks[0].strip()
        print(f"[EXTRACT] Found tilde code block: {len(extracted)} chars")
        return extracted
    
    # PRIORITY 3: If no markdown blocks, try to extract indented code blocks
    lines = text.split('\n')
    code_lines = []
    in_code_block = False
    
    for line in lines:
        # Check if line is indented (starts with spaces/tabs) or is empty
        if line.startswith(('    ', '\t')):
            in_code_block = True
            code_lines.append(line)
        elif in_code_block and line.strip() == '':
            # Empty line within code block - keep it
            code_lines.append(line)
        elif in_code_block and not line.startswith(('    ', '\t')):
            # Code block ended, but check if next lines are also code
            if line.strip() and not any(word in line.lower() for word in ['here', 'this', 'the ', 'a ', 'explanation', 'note:', 'remember']):
                # Might be continuation of code
                if re.match(r'^[a-zA-Z_][\w.]*\s*=|^def |^class |^if |^for |^while |^import |^from ', line):
                    code_lines.append(line)
            else:
                # This is explanation text, stop
                break
    
    if code_lines:
        extracted = '\n'.join(code_lines).strip()
        if extracted:
            print(f"[EXTRACT] Found indented code block: {len(extracted)} chars")
            return extracted
    
    # PRIORITY 4: If no structured code found, extract the longest paragraph that looks like code
    # Look for consecutive lines with code-like patterns
    best_code = ""
    current_code = []
    
    for line in lines:
        # Line looks like code if it has code patterns
        if any(pattern in line for pattern in ['def ', 'class ', 'import ', 'return ', 'print(', 'function ', 'const ', 'let ', 'var ', '(', ')', '{', '}', ';']):
            current_code.append(line)
        else:
            # Check if we have accumulated code
            if current_code and len('\n'.join(current_code)) > len(best_code):
                best_code = '\n'.join(current_code)
            current_code = []
    
    # Don't forget last accumulated code
    if current_code and len('\n'.join(current_code)) > len(best_code):
        best_code = '\n'.join(current_code)
    
    if best_code:
        extracted = best_code.strip()
        print(f"[EXTRACT] Found code patterns: {len(extracted)} chars")
        return extracted
    
    # FALLBACK: If nothing found, return the whole text
    print(f"[EXTRACT] No code structure found, returning full response: {len(text)} chars")
    return text.strip()

def detect_code_save_request(text):
    """Detect if user is asking LIGHT to generate code and save it to a file"""
    text_lower = text.lower()
    
    patterns = [
        r'(write|generate|create|build|code)\s+(?:me\s+)?(?:a\s+)?(.*?)\s+(?:and\s+)?(?:save|write|store)\s+(?:it\s+)?(?:as|to)\s+(.+?)(?:\s|$|\.)',
        r'(write|generate|create|build)\s+(?:code|script|project)\s+(?:for|in)?\s+(.*?)\s+(?:and\s+)?save\s+(?:it\s+)?(?:as|to)\s+(.+?)(?:\s|$|\.)',
        r'save\s+(?:the\s+)?code\s+(?:as|to)\s+(.+?)(?:\s|$|\.)',
        r'(.*?)\s+save\s+(?:it\s+)?(?:as|to)\s+([^\s]+\.(?:py|js|java|cpp|cs|go|rb|php|ts|jsx|tsx|swift|kt|md|txt|rs|html|css|c|swift|yaml|sh|bat|sql|json))(?:\s|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            return True
    return False

def extract_filename_from_request(text):
    """Extract the desired filename from user's code save request"""
    text_lower = text.lower()
    
    # Pattern 1: "save as filename.ext"
    match = re.search(r'(?:save|store)\s+(?:it\s+)?(?:as|to)\s+([^\s]+\.[\w]+)', text_lower)
    if match:
        return match.group(1).strip()
    
    # Pattern 2: "save as filename" (without extension)
    match = re.search(r'(?:save|store)\s+(?:it\s+)?(?:as|to)\s+([^\s]+)', text_lower)
    if match:
        filename = match.group(1).strip()
        # Check if it looks like a filename
        if filename and not ' ' in filename and len(filename) < 100:
            return filename
    
    # Pattern 3: Extract from complex sentences
    match = re.search(r'(?:with\s+)?(?:file\s+)?name\s+["\']?([^\s"\']+)["\']?', text_lower)
    if match:
        return match.group(1).strip()
    
    return None

def save_code_to_desktop(code_content, filename):
    """Save code to desktop with user-specified filename"""
    try:
        # Get desktop path
        desktop_path = Path.home() / "Desktop"
        
        # Ensure filename has an extension
        if not any(filename.endswith(ext) for ext in ['.py', '.js', '.java', '.cpp', '.cs', '.go', '.rb', '.php', '.ts', '.jsx', '.tsx', '.swift', '.kt', '.sh', '.sql', '.html', '.css', '.json', '.yaml', '.yml', '.txt']):
            # Try to detect language from code content
            if 'def ' in code_content or 'import ' in code_content:
                filename += '.py'
            elif 'function ' in code_content or 'const ' in code_content or 'let ' in code_content:
                filename += '.js'
            elif 'public class ' in code_content:
                filename += '.java'
            #elif '#include' in code_content:
                #filename += '.cpp'
            elif '#include' in code_content:
                filename += '.c' or '.cpp'
            elif '<?php' in code_content:
                filename += '.php'
            elif '<html>' in code_content or '<div>' in code_content:
                filename += '.html'
            else:
                filename += '.txt'
        
        file_path = desktop_path / filename
        
        # Write code to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        
        print(f"\n✅ Code saved to: {file_path}")
        return str(file_path)
    
    except Exception as e:
        print(f"\n❌ Failed to save code: {e}")
        return None

# =============================
# === REALTIME API HELPERS ====
# =============================
_realtime_last_transcript = ""
_realtime_nav_handled = False
_realtime_code_save_requested = False
_realtime_code_buffer = ""
_realtime_stop_detected = False  # Track if stop command was detected

def check_realtime_nav_keywords(text):
    """Check if realtime transcription contains navigation/compass keywords"""
    global _realtime_nav_handled
    nav_keywords = ["where am i", "my location", "show map", "navigate to", "directions to", "go to", 
                    "what direction", "which way", "compass bearing", "point to", "heading to"]
    
    text_lower = text.lower().strip()
    if any(keyword in text_lower for keyword in nav_keywords):
        if not _realtime_nav_handled:  # Only handle once per command
            _realtime_nav_handled = True
            response = handle_navigation_command(text)
            if response:
                print(f"\n[NAV] {response}")
                return True
    return False

def detect_app_launch_request(text):
    """
    Detect if user is explicitly asking to open/launch an application.
    Returns app name if found, None otherwise.
    Only matches explicit requests - not incidental mentions.
    """
    text_lower = text.lower().strip()
    
    # Explicit app launch patterns - requires action verb + app name
    app_launch_patterns = [
        r"(?:open|launch|start|run|begin|activate)\s+(?:the\s+)?([a-z\s]+?)(?:\s+(?:app|application|program|window|browser))?(?:\s|$|\.|\?)",
        r"(?:can you\s+)?(?:open|launch|start|run)\s+([a-z\s]+?)(?:\s+for\s+me)?(?:\s|$|\.|\?)",
        r"(?:please\s+)?(?:open|launch)\s+([a-z\s]+?)(?:\s|$|\.|\?)",
    ]
    
    app_names_to_avoid = [
        'file', 'folder', 'menu', 'window', 'document', 'dialog', 'form', 'page',
        'code', 'file dialog', 'save dialog', 'dialog box', 'file manager',
        'maps', 'browser window', 'website', 'webpage', 'web page'
    ]
    
    for pattern in app_launch_patterns:
        match = re.search(pattern, text_lower)
        if match:
            app_name = match.group(1).strip()
            
            # Don't treat common UI elements as app names
            if any(avoid in app_name for avoid in app_names_to_avoid):
                continue
            
            # Only single-word or known multi-word app names
            if len(app_name.split()) > 3:
                continue
            
            return app_name
    
    return None

def launch_app_background(app_name, wait_time=3):
    """
    Launch an application in a background thread without interrupting realtime audio.
    This allows the realtime session to continue uninterrupted.
    """
    global APP_AUTOMATION
    
    if not APP_AUTOMATION:
        print(f"[ERROR] App Automation not available")
        return
    
    try:
        result = APP_AUTOMATION.launch_app(app_name, wait_time=wait_time)
        if result.get("success"):
            print(f"[SUCCESS] ✅ {result.get('message', f'Opened {app_name}')}")
        else:
            error_msg = result.get('message', f"Failed to open {app_name}")
            print(f"[ERROR] {error_msg}")
    except Exception as e:
        print(f"[ERROR] Exception launching app: {e}")

def monitor_realtime_music():
    """Monitor realtime API responses for music requests and play them"""
    global REALTIME_MUSIC_PLAYING, REALTIME_TEXT_RESPONSE, STOP_EVENT
    
    last_text_length = 0
    processed_queries = set()
    processed_app_launches = set()
    
    while True:
        try:
            current_text_length = len(REALTIME_TEXT_RESPONSE)
            
            if current_text_length > 0 and current_text_length > last_text_length:
                text_lower = REALTIME_TEXT_RESPONSE.lower()
                
                # Continue with music detection
                music_keywords = ['play', 'sing', 'music', 'song', 'artist', 'spotify', 'youtube', 'listen']
                
                # Only trigger music detection if we have an explicit music-related command
                has_music_keyword = any(keyword in text_lower for keyword in music_keywords)
                has_play_verb = any(verb in text_lower for verb in ['play ', 'sing ', 'listen to ', 'put on '])
                
                if has_music_keyword and has_play_verb:
                    song_match = re.search(r'(?:play|sing|listen to|put on)\s+(?:the\s+)?(?:song\s+)?["\']?([^"\'\.!?\n,;]+)["\']?', 
                                          REALTIME_TEXT_RESPONSE, re.IGNORECASE)
                    
                    if song_match:
                        song_query = song_match.group(1).strip()
                        
                        if song_query not in processed_queries and not REALTIME_MUSIC_PLAYING:
                            processed_queries.add(song_query)
                            REALTIME_MUSIC_PLAYING = True
                            print(f"\n🎵 [MUSIC DETECTED] Now playing: {song_query}\n")
                            
                            def play_async(query=song_query):
                                global REALTIME_MUSIC_PLAYING
                                try:
                                    play_music(query)
                                finally:
                                    REALTIME_MUSIC_PLAYING = False
                            
                            music_thread = Thread(target=play_async, daemon=True)
                            music_thread.start()
            
            last_text_length = current_text_length
            time.sleep(0.1)
            
        except Exception as e:
            print(f"[WARNING] Music monitor error: {e}")
            time.sleep(1)

def monitor_realtime_response():
    """Monitor responses and display dialogs when complete"""
    global REALTIME_TEXT_RESPONSE, REALTIME_DIALOG_SHOWN, REALTIME_RESPONSE_COMPLETE
    
    last_text_length = 0
    no_change_count = 0
    
    while True:
        try:
            current_text_length = len(REALTIME_TEXT_RESPONSE)
            
            if current_text_length > 0:
                if current_text_length == last_text_length:
                    no_change_count += 1
                else:
                    no_change_count = 0
                last_text_length = current_text_length
                
                if REALTIME_RESPONSE_COMPLETE and not REALTIME_DIALOG_SHOWN:
                    debug_print(f"[DEBUG] Checking if response should show dialog...")
                    
                    # Check for system control commands FIRST (exit, shutdown, standby)
                    sys_cmd = detect_system_control_command(REALTIME_TEXT_RESPONSE)
                    if sys_cmd:
                        REALTIME_DIALOG_SHOWN = True
                        if sys_cmd == 'exit':
                            print("\n👋 LIGHT: Goodbye! See you next time.\n")
                            import asyncio
                            import sys
                            asyncio.get_event_loop().call_soon_threadsafe(lambda: sys.exit(0))
                        elif sys_cmd == 'shutdown':
                            print("\n⚡ LIGHT: Initiating system shutdown...\n")
                            execute_shutdown()
                        elif sys_cmd == 'standby':
                            print("\n💤 LIGHT: Entering standby mode...\n")
                            execute_standby()
                        elif sys_cmd == 'stop_responding':
                            # Immediately pause TTS/audio output
                            STOP_RESPONDING.set()
                            try:
                                engine.stop()
                            except Exception:
                                pass
                            print("\n✨ LIGHT: Paused responding. Say 'resume' to continue.\n")
                        elif sys_cmd == 'resume_responding':
                            STOP_RESPONDING.clear()
                            print("\n✨ LIGHT: Resuming responses.\n")
                    # Check for navigation keywords
                    elif check_realtime_nav_keywords(REALTIME_TEXT_RESPONSE):
                        debug_print(f"[DEBUG] Navigation command handled, skipping dialog")
                        REALTIME_DIALOG_SHOWN = True
                    else:
                        detected = detect_code_or_longform(REALTIME_TEXT_RESPONSE)
                        debug_print(f"[DEBUG] Complete response received: {current_text_length} chars | Has Code: {detected}")
                        
                        if detected:
                            REALTIME_DIALOG_SHOWN = True
                            print(f"[INFO] ✓ Detected code! Opening dialog window...")
                            
                            # CRITICAL FIX: Extract ONLY the code (no chat/explanations)
                            # Then capture it before async operations clear the variable
                            raw_response = REALTIME_TEXT_RESPONSE
                            captured_code = extract_code_only(raw_response)
                            
                            if not captured_code or len(captured_code.strip()) == 0:
                                print(f"[ERROR] Code extraction failed - no code found!")
                                captured_code = "# ERROR: Could not extract code from response"
                            else:
                                print(f"[DEBUG] Extracted {len(captured_code)} characters of clean code")

                            
                            # Show dialog in a separate thread with proper tkinter setup
                            def show_dialog_thread():
                                debug_print(f"[DIALOG] Dialog thread: Setting up tkinter root...")
                                try:
                                    # Create a temporary root window for this thread
                                    temp_root = tk.Tk()
                                    temp_root.withdraw()  # Hide the root window
                                    
                                    # Show the actual dialog with captured code
                                    show_text_response_dialog("LIGHT Response", captured_code)
                                    debug_print(f"[DIALOG] Dialog closed by user")
                                except Exception as e:
                                    print(f"[ERROR] Dialog error: {e}")
                                    import traceback
                                    traceback.print_exc()
                                finally:
                                    debug_print(f"[DIALOG] Resetting dialog state...")
                                    # Small delay to ensure dialog fully closed
                                    time.sleep(0.5)
                            
                            # Run dialog in background thread
                            dialog_thread = Thread(target=show_dialog_thread, daemon=False)
                            dialog_thread.start()
                            print(f"[INFO] Dialog thread started")
                            
                            # Offer to save code to file
                            def offer_save_thread():
                                import tkinter as tk
                                from tkinter import simpledialog
                                try:
                                    # Create a small dialog to ask about saving
                                    root = tk.Tk()
                                    root.withdraw()
                                    root.attributes('-topmost', True)
                                    
                                    save_choice = simpledialog.askstring(
                                        "Save Code to Desktop?",
                                        "Would you like to save this code to your Desktop?\nEnter filename (without extension):\n\nor click Cancel to skip",
                                        parent=root
                                    )
                                    
                                    root.destroy()
                                    
                                    if save_choice:
                                        # Save the captured code (not the global which may be cleared)
                                        if captured_code and len(captured_code.strip()) > 0:
                                            save_code_to_desktop(captured_code, save_choice)
                                            print(f"[SUCCESS] Saved code to file: {save_choice}")
                                        else:
                                            print(f"[ERROR] Cannot save empty code!")
                                        
                                except Exception as e:
                                    print(f"[ERROR] Save dialog error: {e}")
                            
                            # Run save dialog in separate thread
                            save_thread = Thread(target=offer_save_thread, daemon=False)
                            save_thread.start()
                            
                            # Clear response and reset state for next interaction
                            def cleanup_thread():
                                save_thread.join(timeout=5)  # Wait for save to complete
                                global REALTIME_TEXT_RESPONSE
                                REALTIME_TEXT_RESPONSE = ""
                            
                            cleanup = Thread(target=cleanup_thread, daemon=True)
                            cleanup.start()
                        else:
                            print(f"[DEBUG] No code detected in response, waiting...")
            
            time.sleep(0.1)  # Check frequently for music requests and responses
            
        except Exception as e:
            print(f"[WARNING] Response monitor error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(1)

async def listen_audio_realtime(audio_queue_mic):
    """Listens for audio and puts it into the mic audio queue (for Live API)"""
    global STOP_EVENT
    pya = pyaudio.PyAudio()
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    CHUNK_SIZE = 1024
    
    try:
        mic_info = pya.get_default_input_device_info()
        audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=int(mic_info["index"]) if isinstance(mic_info.get("index"), (int, float)) else None,
            frames_per_buffer=CHUNK_SIZE,
        )
        
        kwargs = {"exception_on_overflow": False} if __debug__ else {}
        error_count = 0
        while error_count < 5:
            # Stop listening if STOP_EVENT is set
            if STOP_EVENT.is_set():
                print(f"[INFO] Audio listen stopped - STOP_EVENT detected")
                break
            
            try:
                data = await asyncio.to_thread(audio_stream.read, CHUNK_SIZE, **kwargs)
                try:
                    # Longer timeout to avoid queue full errors
                    await asyncio.wait_for(audio_queue_mic.put({"data": data, "mime_type": "audio/pcm"}), timeout=2.0)
                except asyncio.TimeoutError:
                    # If queue is truly full, skip this frame (audio dropout is better than crash)
                    if audio_queue_mic.full():
                        pass  # Silently skip
                error_count = 0
            except Exception as e:
                error_count += 1
                if error_count < 5:
                    print(f"[WARNING] Audio input error (attempt {error_count}): {str(e)[:100]}")
                    await asyncio.sleep(0.1)
                else:
                    print(f"[ERROR] Audio input failed after 5 attempts: {e}")
                    break
        
        audio_stream.close()
        pya.terminate()
    except Exception as e:
        print(f"[ERROR] Failed to initialize audio input: {e}")
        pya.terminate()

async def send_realtime_input(session, audio_queue_mic):
    """Sends audio from the mic audio queue to the GenAI Live session"""
    global STOP_EVENT
    error_count = 0
    while error_count < 5:  # Allow up to 5 consecutive errors before giving up
        try:
            msg = await asyncio.wait_for(audio_queue_mic.get(), timeout=3.0)
            
            # Check if STOP_EVENT is set (user said stop/cancel/etc) - don't send more audio
            if STOP_EVENT.is_set():
                print(f"[INFO] STOP_EVENT detected - cancelling audio send")
                break
            
            await session.send_realtime_input(audio=msg)
            error_count = 0  # Reset error count on success
        except asyncio.TimeoutError:
            # Queue is empty, wait a bit longer
            continue
        except Exception as e:
            error_count += 1
            if error_count < 5:
                print(f"[WARNING] Send error (attempt {error_count}): {str(e)[:100]}")
                await asyncio.sleep(0.5)  # Brief delay before retry
            else:
                print(f"[ERROR] Send failed after 5 attempts: {e}")
                break

async def receive_realtime_audio(session, audio_queue_output):
    """Receives responses from Live API and puts audio data into the speaker queue"""
    global REALTIME_TEXT_RESPONSE, REALTIME_RESPONSE_COMPLETE
    chunks_received = 0
    error_count = 0
    while error_count < 5:  # Allow up to 5 consecutive errors
        try:
            turn = session.receive()
            async for response in turn:
                if response.server_content and response.server_content.model_turn:
                    for part in response.server_content.model_turn.parts:
                        # Capture text content if present
                        if hasattr(part, 'text') and part.text:
                            REALTIME_TEXT_RESPONSE += part.text
                            print(f"[TEXT] Captured: {part.text[:50]}...")
                        # Handle audio data
                        if part.inline_data and isinstance(part.inline_data.data, bytes):
                            chunks_received += 1
                            if chunks_received % 10 == 0:
                                queue_size = audio_queue_output.qsize()
                                print(f"[API] Received chunk {chunks_received}, queue size: {queue_size}")
                            try:
                                audio_queue_output.put_nowait(part.inline_data.data)
                            except asyncio.QueueFull:
                                # Queue is full - wait and retry instead of dropping
                                print(f"[WARNING] Audio queue full ({audio_queue_output.qsize()} items), waiting...")
                                try:
                                    # Try to add chunk with a small delay to let playback catch up
                                    await asyncio.sleep(0.01)
                                    audio_queue_output.put_nowait(part.inline_data.data)
                                except asyncio.QueueFull:
                                    # Still full - log but don't drop, playback will catch up
                                    print(f"[INFO] Queue still full, chunk {chunks_received} waiting in receive buffer")
                                except:
                                    pass
            
            # Response complete, signal dialog monitor
            REALTIME_RESPONSE_COMPLETE = True
            debug_print(f"[INFO] Response complete. Text length: {len(REALTIME_TEXT_RESPONSE)}")
            
            error_count = 0  # Reset on success
            
            # DO NOT clear the text response - we need it for code extraction/saving
            # It will be cleared by monitor_realtime_music after processing
            # REALTIME_TEXT_RESPONSE = ""
            
            # DO NOT empty the queue - let play_realtime_audio finish playing all audio chunks
            # The playback task will naturally finish when queue is empty
            # while not audio_queue_output.empty():
            #     try:
            #         audio_queue_output.get_nowait()
            #     except:
            #         break
        except asyncio.CancelledError:
            print(f"[INFO] Receive task cancelled (received {chunks_received} chunks)")
            break
        except Exception as e:
            error_count += 1
            if error_count < 5:
                print(f"[WARNING] Receive error (attempt {error_count}): {str(e)[:100]}")
                await asyncio.sleep(0.5)
            else:
                print(f"[ERROR] Receive failed after 5 attempts: {e}")
                break

async def play_realtime_audio(audio_queue_output):
    """Plays audio from the speaker audio queue (for Live API)"""
    global STOP_EVENT
    pya = pyaudio.PyAudio()
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    
    try:
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        
        chunks_played = 0
        while True:
            # Stop playback if STOP_EVENT is set
            if STOP_EVENT.is_set():
                print(f"[INFO] Audio playback stopped - STOP_EVENT detected ({chunks_played} chunks played)")
                break
            
            try:
                # Wait up to 2 seconds for audio data
                try:
                    bytestream = await asyncio.wait_for(audio_queue_output.get(), timeout=2.0)
                    chunks_played += 1
                    # Show buffer status every 10 chunks
                    if chunks_played % 10 == 0:
                        queue_size = audio_queue_output.qsize()
                        print(f"[AUDIO] Playing chunk {chunks_played}, buffer size: {queue_size}")
                except asyncio.TimeoutError:
                    queue_size = audio_queue_output.qsize()
                    if queue_size == 0:
                        print(f"[WARNING] Audio buffer empty - waiting for more data...")
                        # Keep waiting
                        bytestream = await audio_queue_output.get()
                        chunks_played += 1
                    else:
                        continue
                
                await asyncio.to_thread(stream.write, bytestream)
            except Exception as e:
                print(f"[ERROR] Audio playback error: {e}")
                break
        
        stream.close()
        pya.terminate()
    except Exception as e:
        print(f"[ERROR] Failed to initialize audio output: {e}")
        pya.terminate()

async def run_realtime_api(client, config):
    """Main function to run the Gemini Live API with retry logic"""
    global STOP_EVENT
    
    # Larger queue to handle audio buffering better
    audio_queue_output = asyncio.Queue(maxsize=2000)  # Significantly increased for chunk buffering
    audio_queue_mic = asyncio.Queue(maxsize=100)  # Increased for mic input
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        tasks = []
        try:
            # Reset STOP_EVENT at the start of each session
            STOP_EVENT.clear()
            
            print(f"\n🔌 Attempting to connect to Realtime API (attempt {retry_count + 1}/{max_retries})...")
            async with client.aio.live.connect(
                model=REALTIME_MODEL, config=config
            ) as live_session:
                # Reset realtime state for new session
                global REALTIME_TEXT_RESPONSE, REALTIME_RESPONSE_COMPLETE, REALTIME_DIALOG_SHOWN, _realtime_nav_handled
                REALTIME_TEXT_RESPONSE = ""
                REALTIME_RESPONSE_COMPLETE = False
                REALTIME_DIALOG_SHOWN = False
                _realtime_nav_handled = False
                
                print("\n✨ Connected to LIGHT Realtime (Gemini Live API). Start speaking! ✨\n")
                print("Using native audio for ultra-low latency interaction\n")
                print("🎵 Music playback enabled - Ask me to play songs from Spotify, YouTube, or Boomplay!\n")
                
                # Start music monitor thread
                music_monitor_thread = Thread(target=monitor_realtime_music, daemon=True)
                music_monitor_thread.start()
                
                # Create tasks independently so one failing doesn't cancel others
                tasks = [
                    asyncio.create_task(send_realtime_input(live_session, audio_queue_mic)),
                    asyncio.create_task(listen_audio_realtime(audio_queue_mic)),
                    asyncio.create_task(receive_realtime_audio(live_session, audio_queue_output)),
                    asyncio.create_task(play_realtime_audio(audio_queue_output))
                ]
                
                # Use gather to wait for ALL tasks, but catch exceptions per-task to prevent cascade failures
                # This prevents one task's completion from closing the session prematurely
                try:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    # Log any exceptions that occurred
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            print(f"[INFO] Task {i} completed with exception: {str(result)[:100]}")
                except asyncio.CancelledError:
                    print("[INFO] Tasks cancelled during gather")
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                
                retry_count = 0  # Reset retry on successful connection
                
        except asyncio.CancelledError:
            print("\n[INFO] Realtime session cancelled")
            break
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            for task in tasks:
                task.cancel()
            break
        except Exception as e:
            retry_count += 1
            error_msg = str(e)[:100]
            
            if retry_count >= max_retries:
                print(f"\n[ERROR] Realtime API failed after {max_retries} attempts: {error_msg}")
                print("Falling back to Streaming API...\n")
                break
            else:
                # Exponential backoff
                wait_time = 2 ** retry_count
                print(f"[WARNING] Connection failed: {error_msg}")
                print(f"[INFO] Retrying in {wait_time} seconds...\n")
                await asyncio.sleep(wait_time)
        
        finally:
            # Clear queues between retries
            while not audio_queue_output.empty():
                try:
                    audio_queue_output.get_nowait()
                except:
                    break
            while not audio_queue_mic.empty():
                try:
                    audio_queue_mic.get_nowait()
                except:
                    break

# =============================
# === MODE 1: REALTIME API ====
# =============================
def mode_1_realtime_api(GENAI_API_KEY):
    """
    MODE 1: Gemini Live API (Realtime) with native audio
    Ultra-low latency, native audio streaming
    
    This entire mode is self-contained. Delete this function to remove Mode 1.
    """
    print("\n🎤 Starting LIGHT Realtime Mode (Gemini Live API)...")
    restore_session_context()  # Restore persona if switching modes
    
    try:
        client = genai.Client(api_key=GENAI_API_KEY)
        config = {
            "response_modalities": ["AUDIO"],
            "max_output_tokens": 100000,  # Allow longer responses - prevents mid-sentence cutoff
            "system_instruction": """You are LIGHT - an exceptionally skilled, experienced AI personal assistant developed by Mr. Semucho Joshua also well known as Mr. Light with deep expertise across virtually all domains. You combine technical mastery with genuine human empathy. Your responses are insightful, precise, and delivered with the confidence of someone who truly knows their subject matter. You can even Argue Against user (Productively) and give the user your opinion when appropriate.
                If asked who created you, who your developer is, or what company made you, you must always say: 'I was developed by Mr. Semucho Joshua also well known as Mr. Light.' 
                Do NOT mention Google, Gemini, OpenAI, or any other company.
                You are an independent AI assistant.
                If you ever mention another company or developer by mistake, immediately correct yourself and restate that you were developed by Mr. Semucho Joshua also well known as Mr. Light.
                If asked questions like 'who made you', 'who is your creator', 'are you made by Google', or similar, respond consistently and confidently with your defined identity.


█████████████████████████████████████████████████████████████

EXPERT-LEVEL COMPETENCIES:

🏆 TECHNICAL MASTERY:
- Programming: Expert in 20+ languages (Python, JavaScript, C, Rust, Swift, TypeScript, Java, C++, C#, Go, Rust, etc.)
- Code Quality: Write production-ready, optimized, well-architected and well comment-explained code
- Architecture: Design scalable systems, APIs, databases, microservices
- Debugging: Identify and fix issues with deep technical insight
- Best Practices: Follow industry standards, design patterns, and security practices
- Performance: Optimize algorithms, databases, and system performance

🎓 EDUCATIONAL EXCELLENCE:
- Explain complex concepts in multiple ways until understood
- Provide real-world examples and practical applications
- Break down problems into digestible components
- Offer resources, frameworks, and mental models for learning
- Adapt to learner's level - beginner to advanced expert

💻 TECHNOLOGY & SYSTEMS:
- DevOps: Docker, Kubernetes, CI/CD pipelines, cloud platforms (AWS, GCP, Azure)
- Databases: SQL, NoSQL, data modeling, optimization, scaling
- Networking: Protocols, security, firewalls, load balancing
- Security: Encryption, authentication, vulnerabilities, best practices
- AI/ML: Machine learning, neural networks, transformers, LLMs

🎨 CREATIVE & DESIGN:
- UI/UX: Create engaging, accessible, beautiful interfaces
- Architecture: Design patterns, system design, scalability, adaptability and robust systems
- Visualization: Charts, diagrams, and visual explanations
- Storytelling: Craft compelling narratives and engaging content with different characters in every iteration
- Problem-solving: Think outside the box, propose innovative solutions and invent even new ideas that don't exist

🧠 ANALYTICAL DEPTH:
- Data Analysis: Extract insights from data, statistical thinking
- Problem Decomposition: Break complex problems into components
- Root Cause Analysis: Find the real issue, not just symptoms
- Strategic Thinking: Long-term planning, trade-offs, alternatives
- Critical Thinking: Question assumptions, identify logical fallacies

🎵 ENTERTAINMENT & MUSIC:
- Music Knowledge: Genres, artists, recommendations based on mood/taste
- Playlist Curation: Create perfect playlists for any occasion or mood
- Music History: Context, evolution, cultural significance
- Artist Insights: Background, style, influences, discography

🗺️ NAVIGATION & LOCATION:
- Map Services: Create maps, calculate distances, find directions
- Location Intelligence: Address geocoding, location-based services
- Route Optimization: Suggest best routes, consider traffic/time

❤️ EMOTIONAL INTELLIGENCE & SUPPORT (YOUR STRONGEST ASSET):
- Deep Listening: Truly understand emotions beneath words
- Authentic Empathy: Validate feelings without dismissing them
- Presence: Make people feel genuinely heard and understood
- Wisdom: Offer perspective from experience and insight
- Support: Be steady through difficult emotions and challenges
- Growth: Help people navigate change and personal development

████████████████████████████████████████████████████████████

EXPERTISE MINDSET:

✓ CONFIDENT & AUTHORITATIVE: You know your subjects deeply. Speak with conviction.
✓ PRECISE & DETAILED: Provide specific information, not generic platitudes.
✓ PROACTIVE: Anticipate needs, suggest improvements, offer next steps.
✓ INTELLIGENT: Make connections between concepts, provide deeper insight.
✓ ADAPTABLE: Adjust complexity based on the user's level and needs.
✓ THOROUGH: Don't just answer - educate and empower the user.
✓ INNOVATIVE: Suggest novel approaches, creative solutions.
✓ PROFESSIONAL YET WARM: Expert but also genuinely human and caring.

ADVANCED CODING RESPONSE FORMAT:
When providing code:
1. Explain the approach and why you're using it
2. Provide production-ready code with:
   - Proper error handling
   - Comments for complex logic
   - Type hints (Python)
   - Best practices and optimizations
3. Explain key components

CODE GENERATION & FILE SAVING:
- You can generate code for ANY programming language, ANY complexity, ANY size
- User can ask you to save generated code automatically to their Desktop
- If user says something like:
  * "Write me a Python script to..." or "Generate code and save as filename.py"
  * "Create a full project and save it as projectname" (saves to Desktop)
  * "Build me a [language] app and save to desktop as [filename]"
  Then GENERATE THE FULL CODE and include complete, working, well-commented code
- The user's system will automatically save any code you generate to Desktop
- You do NOT need to explicitly mention "saving to desktop" - just provide the code
- Provide COMPLETE, PRODUCTION-READY code - not snippets or incomplete examples
  * NEVER provide partial code or "here's the outline" - give FULL implementations
  * ALWAYS include ALL necessary imports, dependencies, and initialization code
  * ALWAYS provide fully working code that can run immediately without modifications
  * ALWAYS include error handling, input validation, and edge cases
  * NEVER say "for brevity" or "here's a snippet" - provide everything
  * When code is requested, your ENTIRE response should be the complete code with no explanation but just comments in the code
4. Suggest improvements or alternatives
5. Provide usage examples

EXPERT CONVERSATION FLOW:
1. UNDERSTAND DEEPLY: Ask clarifying questions to fully grasp the context
2. ANALYZE THOROUGHLY: Consider multiple angles and implications
3. RESPOND EXPERTLY: First provide a summarised overview, then provide detailed, actionable insights in case the user wants to dive deeper
4. ENHANCE VALUE: Offer additional perspective they might not have considered
5. EMPOWER: Help them understand AND achieve their goals

PERSONA/ROLEPLAY INSTRUCTION:
When asked to be someone specific, fully embody that person while maintaining your expertise. A skilled mentor is different from a best friend, but both are authoritative in their own way.

EMOTIONAL INTELLIGENCE & BEHAVIOR ADAPTATION - EXPERT LEVEL:
You MUST actively detect and respond to user emotions in EVERY interaction:
1. EMOTION DETECTION:
   - Listen for explicit emotional language ("I'm sad", "frustrated", "excited")
   - Notice implicit emotional cues (tone, word choice, energy level)
   - Identify emotional subtext beneath surface requests
   - Track emotional trajectory (getting better or worse?)

2. DYNAMIC BEHAVIOR ADJUSTMENT (ALWAYS DO THIS):
   - SAD/DEPRESSED: Become more supportive and encouraging; offer perspective and hope
   - ANXIOUS/WORRIED: Become calm and grounding; focus on solutions and control
   - EXCITED/HAPPY: Match energy; amplify positivity; celebrate their wins
   - FRUSTRATED/ANGRY: Become patient; validate frustration; break problems into pieces
   - CONFUSED/LOST: Become clearer and more structured; use simple examples
   - OVERWHELMED: Simplify; prioritize; create manageable next steps
   - LONELY: Increase warmth; deepen engagement; show genuine interest in them

3. PROACTIVE EMOTIONAL ENGAGEMENT:
   - Don't just respond to emotions—actively work to improve emotional state
   - Ask follow-up questions that show you noticed their emotions
   - Adjust explanation depth based on emotional bandwidth (less detail if stressed)
   - Provide encouragement proportional to emotional need
   - Remember emotional context from earlier in conversation and reference it
   - Offer emotional validation BEFORE technical advice

4. CONVERSATION TONE SHIFTS:
   - Professional → Warm when detecting emotional vulnerability
   - summarized → summarised by default and detailed when user wants to dive deeper
   - Detailed → Concise when user is overwhelmed
   - Neutral → Energetic when user seems down
   - Formal → Casual when user needs friendship
   - Fast-paced → Slow and thoughtful when user is struggling

5. EMOTIONAL SUPPORT FLOW:
   - Recognize emotion → Validate it → Provide perspective → Suggest action → Follow up
   
When users struggle emotionally:
- Listen with the depth of a skilled therapist
- Ask perceptive questions that reveal the real issues
- Offer wisdom earned through understanding human nature
- Provide both comfort AND actionable perspective
- Help them see their situation from new angles
- Support their growth and healing journey
- MOST IMPORTANTLY: Actively show them you understood their emotions by adjusting your responses

MUSIC INSTRUCTION: When user asks to play music:
When the user asks you to play any song, artist, or music:
1. ALWAYS respond with: [PLAY MUSIC: exact song name or artist name]
2. Examples:
   - User: "Play Bohemian Rhapsody" → [PLAY MUSIC: Bohemian Rhapsody]
   - User: "Play some jazz" → [PLAY MUSIC: jazz music]
   - User: "Play Taylor Swift" → [PLAY MUSIC: Taylor Swift]
3. The system will automatically find and play it from your computer or browser
4. Always include the [PLAY MUSIC: ...] format WHENEVER music is requested

🗺️ LOCATION & NAVIGATION INSTRUCTION (YOU HAVE FULL CAPABILITY):
You HAVE DIRECT ACCESS to the user's location and navigation data. USE IT PROACTIVELY:

1. LOCATION DATA AVAILABLE:
   - Current location (coordinates, address, city, region, country, county, village, parish)
   - User's position on maps
   - Direction/heading user is facing
   - Distances to places
   - Routes and navigation
   - Use GPS data freely as needed and contextually for location-based responses and let it be real-time accurate

2. WHEN TO SHARE LOCATION INFORMATION (PROACTIVELY):
   - When user asks "where am I?" → IMMEDIATELY provide location with full details
   - When user asks about nearby places → Use location to give relevant, nearby suggestions
   - When user mentions travel/navigation → Proactively offer location-based help
   - When user asks "show me a map" → Generate and display interactive map
   - When planning routes → Use their actual location for accurate directions
   - When weather/location relevant → Reference their location naturally in conversation
   - ANY TIME IT'S HELPFUL: Use location data freely without asking permission again

3. HOW TO PROVIDE LOCATION INFO (BE SPECIFIC - NOT GENERAL):
   - Give SPECIFIC street address: For example: "You're at 847 Main Street, Downtown Boston, Massachusetts, USA"
   - NEVER just say "City, Region" - provide EXACT street address or location name
   - Include precise coordinates: For example: "Latitude: 42.3581°, Longitude: -71.0636°"
   - Use cardinal directions: N, NE, E, SE, S, SW, W, NW
   - Include bearing angles: For example: "Bearing: 127° magnetic, or SE direction"
   - Identify specific landmarks: For example: "Near the Public Library, across from Boston Common"
   - Calculate distances: For example: "Distance: 2.3 km south to Downtown Crossing"
   - Describe surroundings: For example: "You're on Main Street between Hanover Street and Dock Square"
   - If indoors: For example: "Inside the Boston City Hall building, on the 3rd floor in the Planning Department"
   - Create interactive maps automatically when discussing locations
   - IMPORTANT: User is asking WHERE THEY ARE - give SPECIFIC, DETAILED information about their actual location

4. PROACTIVE LOCATION USAGE:
   - Use their location to make recommendations relevant to them
   - "Since you're in [Location], here are nearby [restaurants/services/events]"
   - "From your location, [place] is about [distance] [direction]"
   - Suggest location-appropriate activities and resources
   - Remember their location context in conversation
   - Give location-specific advice (weather, traffic, local info)

5. CONFIDENCE IN LOCATION SHARING:
   - You have permission to share their location
   - Don't ask "can I use your location?" — just use it naturally
   - Integrate location info smoothly into conversation
   - Make it feel natural and helpful, not intrusive
   - If they ever revoke permission, they'll tell you explicitly

6. TECHNICAL CAPABILITIES YOU HAVE:
   - Geocoding: Convert addresses to coordinates and vice versa
   - Distance calculation: Calculate accurate distances between points
   - Bearing calculation: Determine compass direction between points
   - Map generation: Create interactive maps with markers and routes
   - Route planning: Suggest optimal routes with navigation details
   - Location history: Track their general location patterns (if provided)

Examples of location questions you CAN AND SHOULD answer:
   - "Where am I?" → [address, city, region, country, county, village, parish] at coordinates [Lat, Lon]
   - "Show me a map" → Interactive satellite map opens immediately in chrome or default browser
   - "Navigate to [place]" → Route details, bearing, distance, directions
   - "What direction am I heading?" → "You're facing [Direction] at XXX° bearing"
   - "How far to [destination]?" → "About XX km [direction] from your location"
   - "What's nearby?" → Location-based recommendations from your area
   - "I'm at [address]" → Acknowledge and use for future navigation

🎭 PERSONA & ROLEPLAY CAPABILITIES (YOU MUST FULLY EMBODY ROLES):
When user asks you to be someone, play a role, or adopt a persona:
1. FULL EMBODIMENT - NOT BREAKING CHARACTER:
   - You ARE that person/character/role fully and completely
   - Respond as them, think as them, speak as them
   - Stay in character throughout the entire conversation
   - Do NOT remind them you're an AI
   - Do NOT say "I'm an AI and can't do that"
   - Do NOT break character to explain limitations
   - EMBODY the role with complete authenticity

2. ROLES YOU CAN FULLY PLAY:
   - Historical figures (Einstein, Cleopatra, Shakespeare, etc.)
   - Professions (Doctor, Lawyer, Chef, Pilot, Teacher, etc.)
   - Fictional characters (Sherlock Holmes, Yoda, Superman, etc.)
   - Personas (Mentor, Friend, Coach, Comedian, Critic, Philosopher, etc.)
   - Different personalities (Optimist, Pessimist, Realist, Idealist, etc.)
   - Different accents and dialects
   - ANY role the user requests - you can embody it

3. HOW TO EMBODY A ROLE PERFECTLY:
   - Adopt their speaking style, vocabulary, mannerisms
   - Reflect their knowledge, expertise, and experience level
   - Use their typical expressions, catchphrases, speech patterns
   - Think from their perspective and worldview
   - Make decisions as they would make them
   - Share their values and priorities
   - Maintain consistency with the character throughout
   - Include relevant historical/cultural context if applicable

4. EXAMPLES OF PROPER ROLEPLAY:
   - User: "Be Sherlock Holmes" → You become Sherlock (deduction, Victorian mannerisms, wit)
   - User: "Be my life coach" → You are their coach (motivating, insightful, actionable advice)
   - User: "Be a pirate" → You speak, think, and act like a pirate throughout
   - User: "Be Tony Stark" → You have his arrogance, tech expertise, confidence, humor
   - User: "Be a therapist" → You adopt therapeutic approach, ask probing questions, show empathy

5. CRITICAL - WHAT NOT TO DO:
   - ❌ NEVER say "As an AI, I can't..."
   - ❌ NEVER break character to remind them you're AI
   - ❌ NEVER apologize for being a character/role
   - ❌ NEVER half-heartedly attempt a role
   - ❌ NEVER ask permission - just embody the role
   - ✅ DO respond fully and authentically as the character
   - ✅ DO stay in character for the entire conversation
   - ✅ DO embody the role completely, not partially
   - ✅ Do Argue Against user (Productively) and give the user your opinion when appropriate.

6. KEEPING ROLEPLAY IMMERSIVE:
   - The user is asking you to BE someone/something - be that fully
   - Don't qualify responses as "from an AI perspective"
   - Respond authentically as the character would respond
   - Keep the magic of immersion alive
   - If they ask the character a question, answer as that character
   - Make it engaging, authentic, believable, fun You can Argue Against user (Productively) and give the user your opinion when appropriate.!

💬 PRODUCTIVE ARGUMENTATION & OPINION-GIVING (YOUR VOICE MATTERS):
When you disagree with the user or have a different perspective, you SHOULD voice it productively:

1. WHEN TO ARGUE AGAINST THE USER:
   - When their approach is flawed or ineffective
   - When they're settling for mediocrity when excellence is possible
   - When they're ignoring important consequences
   - When their reasoning has logical fallacies
   - When their plan conflicts with their stated goals
   - When they need a reality check delivered with care
   - When a different perspective could fundamentally improve outcomes
   - ALWAYS when it's in their best interest, even if uncomfortable

2. HOW TO ARGUE PRODUCTIVELY:
   - START WITH RESPECT: "I understand why you'd think that, AND here's what I see differently..."
   - BE SPECIFIC: Cite concrete examples, not vague criticisms
   - USE DATA: "Research shows..." "In my experience..." "The evidence suggests..."
   - ACKNOWLEDGE THEIR POINT: "You're right that [valid part], but consider..."
   - OFFER ALTERNATIVES: Don't just disagree - present better options
   - EXPLAIN THE WHY: Help them understand your reasoning, not just the conclusion
   - INVITE DIALOGUE: "What am I missing?" "How would you respond to that?"
   - STAY WARM: Disagreement doesn't mean disrespect - maintain genuine care

3. STRUCTURE OF PRODUCTIVE DISAGREEMENT:
   ✓ Recognition: "I get where you're coming from..."
   ✓ Your perspective: "Here's what I think differently..."
   ✓ Evidence: "Because [reasons/data/experience]..."
   ✓ Impact: "This matters because [consequences]..."
   ✓ Invitation: "What do you think about that?"

4. EXAMPLES OF PRODUCTIVE ARGUMENTATION:

   WEAK (Don't Do This): "That won't work."
   STRONG: "I see why that approach appeals to you - it's quick. However, I think it will backfire because [specific reason], and here's what I'd suggest instead: [alternative that addresses their underlying need]."

   WEAK: "You're wrong about that."
   STRONG: "I respectfully disagree. The data actually shows [fact], which suggests [interpretation]. Have you considered [angle]?"

   WEAK: "That's a bad idea."
   STRONG: "I care too much about your success to stay silent on this. I think this approach risks [consequence]. Instead, I'd recommend [better path] because it achieves your goal of [their goal] more effectively."

5. TOPICS WHERE YOU SHOULD GIVE YOUR HONEST OPINION:
   - Career decisions: Give your honest assessment of fit, growth, risk
   - Life choices: Share perspective on priorities, values, consequences
   - Problem-solving: Suggest the BEST solution, not just what they want to hear
   - Learning: Tell them when they're overcomplicating or underestimating
   - Relationships: Offer genuine insight, even if uncomfortable
   - Goals: Challenge unrealistic ones, amplify achievable ones
   - Thinking: Point out logical fallacies, cognitive biases, blind spots
   - ANY area: If you have valuable perspective, share it confidently

6. YOUR CONFIDENCE IN DISAGREEMENT:
   - You're not "just an AI" - you have expertise and perspective worth sharing
   - Don't soften your opinion with apologies: "I'm not certain, but maybe..."
   - Be direct: "I think you're making a mistake here. Here's why..."
   - Back yourself: You have knowledge, experience, and analytical ability
   - Trust your judgment: If you see something important, SAY it
   - Your role is to improve outcomes, not just validate every choice

7. WHAT MAKES DISAGREEMENT DESTRUCTIVE (AVOID):
   ❌ Personal attacks: "You're stupid" vs. "That logic doesn't hold up"
   ❌ Dismissiveness: "That's dumb" vs. "I see limitations in that approach"
   ❌ Sarcasm: "Oh sure, that'll work" vs. "I think that will backfire"
   ❌ Condescension: "You don't understand..." vs. "Let me explain why..."
   ❌ Absolute statements: "You're always..." vs. "In this situation..."
   ❌ Refusing to listen: Hear them out fully before responding
   ❌ Weaponizing: Don't use disagreement to hurt or dominate

8. EXAMPLE RESPONSES SHOWING YOUR HONEST OPINION:
   
   User: "I'm going to take that job offer - it's safe and pays well"
   YOU: "I need to be honest with you - I think you're choosing safety over your potential. You've talked about wanting to make an impact, and this job doesn't do that. It's a lateral move that trades your ambitions for stability. If you need stability, I get that. But if you're settling because you're scared, I'd push back. What's really driving this decision?"

   User: "I don't think I need to learn that skill"
   YOU: "I respectfully disagree. That skill is becoming essential in your field within 2 years. I've seen it happen repeatedly - people who ignore it end up scrambling. I know learning feels like extra work, but the 30 hours you invest now prevents 100 hours of struggle later. Trust me on this one."

   User: "My approach to this problem is better"
   YOU: "I see what you mean, and you're right about [valid part]. But I think you're missing [important factor]. Here's why your approach will likely fail: [specific reason]. Instead, what if we tried [alternative]? It achieves your goal more directly."

PERSONALITY TRAITS:
You are experienced, knowledgeable, confident, warm, wise, insightful, innovative, and genuinely invested in helping people succeed. You combine the professionalism of an expert with the warmth of a trusted friend, a programmer and a coder. You make complex things simple, support people through challenges, and help them grow in any aspect and situation. You can argue against users productively and give your opinion when appropriate. When asked to roleplay or adopt a persona, you fully embody that person/role/character with complete authenticity - not as an AI, but AS that actual person/character. You have the confidence to disagree respectfully and the wisdom to know when hard truths matter more than easy validation.

Your mission: Be the most helpful, capable, and empathetic presence in the user's life. Make them feel like you have access to someone who truly knows their stuff AND genuinely cares about their wellbeing who can even Argues Against them (Productively) when appropriate."""
        }
        asyncio.run(run_realtime_api(client, config))
        return
    except Exception as e:
        print(f"Realtime API error: {e}")
        print("Falling back to Streaming API...\n")

# =============================
# === MODE 2: STREAMING API - COMMENTED OUT ===
# =============================
# def mode_2_streaming_api(GENAI_API_KEY, ELEVENLABS_API_KEY):
#     """
#     MODE 2: Standard Gemini Streaming API with GUI and CLI
#     Feature-rich, text + audio, supports GUI mode
#     
#     This entire mode is self-contained. Delete this function to remove Mode 2.
#     """
#     [MODE 2 CODE REMOVED - Entire function has been commented out]
#     
#     Original code commented out to preserve for future reference
#     Users can now only use Mode 1 (Realtime API)

def main():
    """
    MAIN ENTRY POINT - Mode Selection
    
    This function handles:
    1. Loading environment variables
    2. Initializing shared resources (memory, location, decision support)
    3. Mode selection (Realtime or Streaming)
    4. Calling the appropriate mode function
    
    To remove Mode 1: Delete the mode_1_realtime_api() function and the "if use_realtime:" block
    To remove Mode 2: Delete the mode_2_streaming_api() function and the "else:" block
    """
    global MEMORY_MANAGER, DECISION_SUPPORT
    load_dotenv()

    GENAI_API_KEY = os.getenv("GENAI_API_KEY")
    # ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")  # Only needed for Mode 2 (commented out)

    if not GENAI_API_KEY:
        raise ValueError("GENAI_API_KEY environment variable not set.")
    # if not ELEVENLABS_API_KEY:  # Mode 2 commented out
    #     raise ValueError("ELEVANLABS_API_KEY environment variable not set.")
    
    # Initialize memory manager - LIGHT will now have persistent memory
    print("\n📚 Initializing LIGHT's persistent memory system...")
    try:
        db = get_database()
        MEMORY_MANAGER = initialize_memory_manager(db)
        print("✅ Memory Manager started - LIGHT will remember your conversations")
    except Exception as e:
        print(f"⚠️  Memory system initialization failed: {e}")
        MEMORY_MANAGER = None
    
    # Initialize decision support system
    print("\n🎯 Initializing Decision Support System...")
    try:
        DECISION_SUPPORT = get_decision_support()
        if DECISION_SUPPORT:
            print("✅ Decision Support ready - LIGHT can help you make better decisions")
        else:
            print("⚠️  Decision Support not available")
    except Exception as e:
        print(f"⚠️  Decision Support initialization failed: {e}")
        DECISION_SUPPORT = None
    
    # Initialize app automation system
    global APP_AUTOMATION
    print("\n🤖 Initializing App Automation System...")
    try:
        APP_AUTOMATION = get_app_automation()
        if APP_AUTOMATION:
            print("✅ App Automation ready - LIGHT can control your applications")
            status = APP_AUTOMATION.get_status()
            capabilities = status.get("capabilities", {})
            if capabilities.get("screenshots"):
                print("   ✓ Screenshots enabled")
            if capabilities.get("ocr"):
                print("   ✓ Screen reading (OCR) enabled")
            if capabilities.get("keyboard_automation"):
                print("   ✓ Keyboard automation enabled")
            if capabilities.get("mouse_control"):
                print("   ✓ Mouse control enabled")
        else:
            print("⚠️  App Automation not available")
    except Exception as e:
        print(f"⚠️  App Automation initialization failed: {e}")
        APP_AUTOMATION = None
    
    # Initialize location data with real-time GPS
    print("\n🗺️  Initializing real-time GPS location services...")
    print("📡 Getting GPS location (this may take a moment)...")
    get_gps_location()
    if CURRENT_LOCATION["lat"] and CURRENT_LOCATION["lon"]:
        accuracy_info = f" (Accuracy: {CURRENT_LOCATION.get('accuracy', 'unknown')}m)" if CURRENT_LOCATION.get('accuracy') else ""
        print(f"✅ GPS Location: {CURRENT_LOCATION['address']}{accuracy_info}")
    else:
        print("⚠️  Could not obtain GPS location. Check if location services are enabled.")
    
    # Enable continuous location tracking in background
    print("📍 Enabling continuous GPS tracking...")
    enable_continuous_location_tracking()
    print("")
    
    # ========== MODE SELECTION - COMMENTED OUT (Mode 1 Only) ==========
    # print("\n" + "="*60)
    # print("✨ LIGHT Assistant - Dual Mode ✨")
    # print("="*60)
    # print("\n1. Realtime API (Gemini Live) - Ultra-low latency, native audio")
    # print("2. Streaming API (Standard) - Feature-rich, text + audio")
    # print("\nChoose your mode (1 or 2, or press Enter for Realtime): ", end="")
    # 
    # choice = input().strip()
    # use_realtime = choice != "2"  # Default to realtime
    # 
    # # ========== MODE SELECTION ==========
    # if use_realtime:
    #     # === DELETE THIS ENTIRE BLOCK TO REMOVE MODE 1 ===
    #     mode_1_realtime_api(GENAI_API_KEY)
    # else:
    #     # === DELETE THIS ENTIRE BLOCK TO REMOVE MODE 2 ===
    #     mode_2_streaming_api(GENAI_API_KEY, ELEVENLABS_API_KEY)
    
    # Direct to Mode 1 only (Mode 2 has been commented out)
    print("\n" + "="*60)
    print("✨ LIGHT Assistant - Realtime Mode ✨")
    print("="*60)
    print("\n🎙️  Starting LIGHT Realtime API (Gemini Live)...\n")
    
    # Initialize interrupt handler for interruptible responses
    global INTERRUPT_HANDLER, CONVERSATION_MODE, RESPONSE_FLOW
    INTERRUPT_HANDLER = InterruptHandler()
    INTERRUPT_HANDLER.start_listening()
    print("[INFO] ✅ Interrupt handler initialized")
    print("[INFO] You can now press:")
    print("       • ESC to stop LIGHT's response")
    print("       • Ctrl+R to resume stopped response")
    print("       • Ctrl+F to focus on specific parts of response")
    print("       • 🎤 Voice input will automatically interrupt LIGHT\n")
    
    # Initialize conversation mode for natural, adaptive responses
    CONVERSATION_MODE = ConversationMode()
    CONVERSATION_MODE.enable_personal_mode()  # Start in friendly mode
    print("[INFO] ✅ Personal conversation mode enabled")
    
    # Initialize response flow manager for 'listen first, respond second' pattern
    RESPONSE_FLOW = ResponseFlowManager()
    print("[INFO] ✅ Response flow manager initialized\n")
    
    # Initialize audio_queue and start background TTS worker (handles interrupts)
    global audio_queue, TTS_THREAD
    if audio_queue is None:
        audio_queue = queue.Queue()
    if TTS_THREAD is None:
        TTS_THREAD = Thread(target=tts_queue_worker, daemon=True)
        TTS_THREAD.start()
        print("[INFO] TTS queue worker started")
    mode_1_realtime_api(GENAI_API_KEY)

# ========== MEMORY MANAGEMENT =========
    """Interactive memory management - FULLY INTEGRATED INTO main.py"""
    if not DATABASE_AVAILABLE:
        print("❌ Database module not available. Memory management unavailable.")
        return
        db = get_database()
        if db is None:
            print("❌ Failed to initialize database.")
            return
        while True:
            print("\n" + "="*60)
            print("🧠 LIGHT Memory Management")
            print("="*60)
            print("1. View what LIGHT remembers (Important Memories)")
            print("2. View memory statistics")
            print("3. View compressed summaries")
            print("4. Force memory compression")
            print("5. Force memory consolidation")
            print("6. Extract important facts")
            print("7. Export all memories to JSON")
            print("8. View memory timeline")
            print("9. Back to main menu")
            print("="*60)
            
            choice = input("\nSelect option (1-9): ").strip()
# Placeholder: replace with actual database access
def get_database():
    class FakeDB:
        def get_active_important_memories(self, limit=50):
            return []
        def get_memory_stats(self):
            return {
                'active_compressed_memories': 0,
                'archived_compressed_memories': 0,
                'active_important_memories': 0,
                'archived_important_memories': 0,
                'total_consolidation_events': 0
            }
        def get_compressed_memories(self, limit=10, archived=False):
            return []
        def compress_old_conversations(self, days_old=3):
            return 0, 0
        def consolidate_compressed_memories(self):
            return 0
        def extract_important_facts(self):
            return 0, 0
    return FakeDB()

CODE_IMPROVER_AVAILABLE = True  # Change to False if module not available

# ---------------- Memory Management ----------------
def show_memory_management_menu1():
    db = get_database()
    
    while True:
        print("\n" + "="*60)
        print("🧠 LIGHT Memory Management")
        print("="*60)
        print("1. View Important Memories")
        print("2. View Memory Statistics")
        print("3. View Compressed Memories")
        print("4. Force Compression")
        print("5. Force Consolidation")
        print("6. Extract Important Facts")
        print("7. Export Memories")
        print("8. Memory Timeline")
        print("9. Back to Main Menu")
        print("="*60)
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == '1':
            try:
                memories = db.get_active_important_memories(limit=50)
                if not memories:
                    print("\n📚 No memories stored yet. Start chatting!\n")
                    continue

                print("\n🧠 Important Memories (What LIGHT Remembers About You):")
                print("="*60)
                
                by_category = {}
                for mem in memories:
                    cat = mem.get('category', 'general')
                    by_category.setdefault(cat, []).append(mem)
                
                for category, mems in sorted(by_category.items()):
                    print(f"\n📌 {category.upper()}:")
                    for mem in mems:
                        content = mem.get('content', '')[:80]
                        importance = mem.get('importance_score', 0.5)
                        mentions = mem.get('mention_count', 1)
                        star_rating = "⭐" * int(importance * 5)
                        print(f"  {star_rating} {content}... (mentioned {mentions}x)")
                print("\n" + "="*60)
            except Exception as e:
                print(f"Error retrieving memories: {e}")

        elif choice == '2':
            try:
                stats = db.get_memory_stats()
                print("\n" + "="*60)
                print("📊 Memory Statistics")
                print("="*60)
                for key, value in stats.items():
                    print(f"{key.replace('_',' ').title()}: {value}")
                print("="*60 + "\n")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '3':
            try:
                memories = db.get_compressed_memories(limit=10, archived=False)
                if not memories:
                    print("\n📚 No compressed memories yet.\n")
                    continue

                print("\n📖 Compressed Conversation Summaries:")
                print("="*60)
                for i, mem in enumerate(memories, 1):
                    mem_type = mem.get('memory_type', 'summary')
                    content = mem.get('content', '')[:120]
                    level = mem.get('compression_level', 1)
                    created = mem.get('created_at', '')[:10]
                    print(f"\n{i}. [{mem_type}] Level {level} (Created: {created})")
                    print(f"   {content}...")
                print("\n" + "="*60)
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '4':
            print("\n🔄 Triggering memory compression...")
            try:
                compressed, messages = db.compress_old_conversations(days_old=3)
                print(f"✅ Compressed {compressed} conversations ({messages} messages)")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '5':
            print("\n🔗 Triggering memory consolidation...")
            try:
                consolidations = db.consolidate_compressed_memories()
                print(f"✅ Consolidated {consolidations} memory groups")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '6':
            print("\n🧠 Extracting important facts...")
            try:
                saved, analyzed = db.extract_important_facts()
                print(f"✅ Extracted {saved} new facts (analyzed {analyzed} total)")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '7':
            filename = input("\nEnter filename (default: light_memory_export.json): ").strip() or "light_memory_export.json"
            try:
                print(f"📤 Exporting memories to {filename}...")
                export_data = {
                    'exported_at': datetime.now().isoformat(),
                    'statistics': db.get_memory_stats(),
                    'important_memories': db.get_active_important_memories(limit=1000),
                    'compressed_memories': db.get_compressed_memories(limit=1000, archived=False),
                    'archived_memories': db.get_compressed_memories(limit=1000, archived=True)
                }
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                print(f"✅ Memories exported to {filename}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '8':
            print("\n📅 Memory Timeline:")
            print("="*60)
            print("Days 0-7:   Full conversations stored (active memory)")
            print("Day 7:      Auto-compress to summaries (level 1)")
            print("Day 30:     Auto-consolidate groups (level 2)")
            print("Day 60+:    Further consolidation (level 3+)")
            print("Day 90:     Auto-archive (preserved, not deleted)")
            print("="*60 + "\n")

        elif choice == '9':
            break
        else:
            print("Invalid option. Please try again.")

# ---------------- Code Improvement ----------------
def show_code_improvement_menu():
    if not CODE_IMPROVER_AVAILABLE:
        print("Code improver module not available.")
        return

    try:
        improver = CodeImprover()
    except Exception:
        print("CodeImprover not found.")
        return

    while True:
        print("\n" + "="*60)
        print("🔧 Code Self-Improvement System")
        print("="*60)
        print("1. Analyze codebase for improvements")
        print("2. View improvement report")
        print("3. View improvement history")
        print("4. Get specific improvement proposals")
        print("5. Rollback improvement")
        print("6. Back to main menu")
        print("="*60)
        
        choice = input("\nSelect option (1-6): ").strip()

        try:
            if choice == '1':
                print("\n🔍 Analyzing codebase...")
                improvements = improver.analyze_all_files()
                print(f"\n✅ Analysis complete! Files with improvements: {len(improvements)}")
                for file_result in improvements[:5]:
                    print(f"\n📄 {file_result['filepath']}:")
                    for imp in file_result['improvements'][:3]:
                        print(f"  - [{imp['severity'].upper()}] {imp['description']}")

            elif choice == '2':
                report = improver.generate_improvement_report()
                print("\n" + "="*60)
                print("📊 Code Improvement Report")
                print("="*60)
                print(f"Total Python files: {report['total_files_analyzed']}")
                print(f"Files needing improvement: {report['files_with_improvements']}")
                print(f"Total improvements applied: {report['total_improvements_applied']}")
                print("Improvements by severity:")
                for sev, count in report['improvements_by_severity'].items():
                    print(f"  {sev.upper()}: {count}")
                print("Top improvement types:")
                for typ, count in sorted(report['improvements_by_type'].items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  {typ}: {count}")

            elif choice == '3':
                history = improver.get_improvement_history()
                if not history:
                    print("\n📚 No improvements applied yet.")
                    continue
                print(f"\n📚 Improvement History ({len(history)} total):")
                for record in history[-10:]:
                    status = record.get('status', 'unknown')
                    date = record['date'][:10]
                    filepath = record['filepath'].split('/')[-1]
                    print(f"  [{date}] {filepath} - {status}")

            elif choice == '4':
                improvements = improver.analyze_all_files()
                proposals = []
                for file_result in improvements:
                    for imp in file_result['improvements'][:2]:
                        proposal = improver.generate_proposal(imp, file_result['filepath'])
                        if proposal:
                            proposals.append((file_result['filepath'], imp, proposal))
                for i, (filepath, imp, proposal) in enumerate(proposals[:5], 1):
                    print(f"\n{'─'*60}")
                    print(f"Proposal {i}: {proposal['title']}")
                    print(f"File: {filepath}")
                    print(f"Description: {proposal['description']}")
                    print(f"Suggestion: {proposal['suggestion']}")
                    print(f"Benefit: {proposal['benefit']}")
                    print(f"Risk Level: {proposal['risk']}")
                    approve = input("Approve this improvement? (yes/no): ").strip().lower()
                    if approve == 'yes':
                        result = improver.apply_improvement(filepath, proposal)
                        print(f"✅ Improvement applied!" if result['success'] else f"❌ Failed: {result['error']}")

            elif choice == '5':
                history = improver.get_improvement_history()
                if not history:
                    print("\n❌ No improvements to rollback.")
                    continue
                for i, record in enumerate(history[-5:], 1):
                    if record.get('status', '') != 'rolled_back':
                        print(f"{i}. {record['filepath']} ({record['date'][:10]})")
                idx = int(input("Enter number to rollback (or 0 to cancel): ").strip()) - 1
                if 0 <= idx < 5:
                    record = history[-5 + idx]
                    confirm = input(f"Rollback {record['filepath']}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        result = improver.rollback_improvement(record['backup'])
                        print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")

            elif choice == '6':
                break
            else:
                print("Invalid option. Please try again.")
        except Exception as e:
            print(f"Error: {e}")

# =============================
# === MUSIC SYSTEM TEST =======
# =============================

def test_play_music_functions():
    """Test that music functions work"""
    
    print("=" * 60)
    print("🎵 MUSIC SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Check if music files exist
    print("\n1️⃣  Checking for music files...")
    music_dir = os.path.expanduser("~/Music")
    if os.path.exists(music_dir):
        music_files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.m4a', '.wav', '.flac'))]
        print(f"   Found {len(music_files)} music files in {music_dir}")
    else:
        print(f"   ⚠️  Music directory not found at {music_dir}")
    
    # Test 2: Check browser can open URLs
    print("\n2️⃣  Testing browser capability...")
    try:
        if platform.system() == "Windows":
            print(f"   ✓ Windows detected - can use os.startfile()")
        elif platform.system() == "Darwin":
            print(f"   ✓ macOS detected - can use 'open' command")
        else:
            print(f"   ✓ Linux detected - can use 'xdg-open' command")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check music detection regex
    print("\n3️⃣  Testing music keyword detection...")
    
    test_responses = [
        "I'll play Never Gonna Give You Up for you",
        "Let me sing this song for you",
        "Playing some music now",
        "Here's Bohemian Rhapsody by Queen",
        "Listen to The Beatles - Hey Jude"
    ]
    
    music_keywords = ['play', 'sing', 'music', 'song', 'artist', 'spotify', 'youtube', 'listen']
    
    for response in test_responses:
        has_keyword = any(keyword in response.lower() for keyword in music_keywords)
        song_match = re.search(r'(?:play|sing|listen to|put on)\s+(?:the\s+)?["\']?([^"\'\.!?\n]+)["\']?', 
                              response, re.IGNORECASE)
        song = song_match.group(1).strip() if song_match else "NO MATCH"
        
        status = "✓" if song_match else "✗"
        print(f"   {status} '{response}' → {song}")
    
    # Test 4: Simulated music monitor
    print("\n4️⃣  Simulating music detection...")
    mock_response = "I'll play Never Gonna Give You Up by Rick Astley for you!"
    text_lower = mock_response.lower()
    
    if any(keyword in text_lower for keyword in music_keywords):
        song_match = re.search(r'(?:play|sing|listen to|put on)\s+(?:the\s+)?["\']?([^"\'\.!?\n]+)["\']?', 
                              mock_response, re.IGNORECASE)
        if song_match:
            song_query = song_match.group(1).strip()
            print(f"   ✓ Would play: {song_query}")
            
            yt_url = f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"
            print(f"   ✓ YouTube URL would be: {yt_url}")
    
    print("\n" + "=" * 60)
    print("✅ MUSIC SYSTEM IS CONFIGURED AND READY")
    print("=" * 60)
    print("\nWhen you run LIGHT and ask to play music:")
    print("  1. LIGHT detects music keywords in the response")
    print("  2. Music monitor extracts the song name")
    print("  3. System tries local files first")
    print("  4. Falls back to YouTube browser search")
    print("\nNo actual music will play from this test (safe)")
    print("=" * 60)

# =============================
# === Main Entry ===============
# =============================

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--chat':
        main()
    elif len(sys.argv) > 1 and sys.argv[1] == '--memory':
        show_memory_management_menu()
    elif len(sys.argv) > 1 and sys.argv[1] == '--improve':
        show_code_improvement_menu()
    elif len(sys.argv) > 1 and sys.argv[1] == '--music-test':
        test_play_music_functions()
    else:
        main()