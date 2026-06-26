import os
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Local persistent profile folder to store cookies and login state
USER_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'user_data'))

_shared_driver = None
_auto_reply_active = False

def get_edge_driver(headless=False):
    options = webdriver.EdgeOptions()
    options.add_argument(f"user-data-dir={USER_DATA_DIR}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edge/120.0.0.0")
    
    if headless:
        options.add_argument("--headless=new")
        
    driver = webdriver.Edge(options=options)
    return driver

def get_shared_driver(headless=False):
    global _shared_driver
    if _shared_driver:
        try:
            if _shared_driver.window_handles:
                return _shared_driver
        except Exception:
            try:
                _shared_driver.quit()
            except Exception:
                pass
            _shared_driver = None
            
    _shared_driver = get_edge_driver(headless=headless)
    return _shared_driver

def check_login_status(driver, timeout=15):
    """
    Check if the session is logged in.
    Returns:
      True if logged in (chat pane loaded)
      False if on login screen (QR code canvas or scan instruction loaded)
      None if status is indeterminate or timed out
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if not driver.window_handles:
                raise Exception("Browser window was closed by the user.")
        except Exception:
            raise Exception("Browser window was closed by the user.")
            
        # Check for chat pane (logged in)
        if driver.find_elements(By.XPATH, '//div[@id="pane-side"] | //div[@data-testid="chat-list-search"]'):
            return True
            
        # Check for login QR canvas or Scan QR text
        if driver.find_elements(By.XPATH, '//canvas | //div[@data-testid="qrcode"] | //*[contains(text(), "Scan QR code")]'):
            return False
            
        time.sleep(0.5)
        
    return None

def open_chat_with_target(driver, wait, target):
    is_number = target.isdigit() or (target.startswith('+') and target[1:].isdigit())
    
    if is_number:
        cleaned_num = "".join(c for c in target if c.isdigit())
        url = f"https://web.whatsapp.com/send?phone={cleaned_num}"
        print(f"\n[JARVIS]: Navigating directly to chat with number: {cleaned_num}...")
        driver.get(url)
        
        # Verify if number is invalid or if send/input box loads
        start_time = time.time()
        invalid_popup = False
        loaded = False
        while time.time() - start_time < 30:
            try:
                if not driver.window_handles:
                    return "Error: Browser window was closed by the user."
            except Exception:
                return "Error: Browser window was closed by the user."
                
            # Check if input box loaded
            inputs = driver.find_elements(By.XPATH, '//div[@data-testid="conversation-compose-box-input"] | //div[@id="main"]//footer//div[@contenteditable="true"]')
            if inputs:
                loaded = True
                break
                
            # Check for invalid phone number dialog
            popups = driver.find_elements(By.XPATH, '//*[contains(text(), "invalid") or contains(text(), "not exist") or contains(text(), "OK")]')
            for pop in popups:
                if "invalid" in pop.text.lower() or "ok" in pop.text.lower():
                    invalid_popup = True
                    break
            if invalid_popup:
                break
            time.sleep(1)
            
        if invalid_popup:
            return f"Error: The phone number '{target}' is not registered on WhatsApp or is invalid."
        if not loaded:
            return "Error: Failed to load the chat session (timeout)."
        return "Success"
    else:
        # Search contact
        print("[JARVIS]: Locating chat search box...")
        search_box_xpath = '//input[@placeholder="Search or start a new chat"] | //input[contains(@placeholder, "Search")] | //div[@data-testid="chat-list-search"]//input | //*[@role="textbox"]'
        search_box = wait.until(EC.element_to_be_clickable((By.XPATH, search_box_xpath)))
        
        print(f"[JARVIS]: Searching for contact: '{target}'...")
        search_box.click()
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.BACKSPACE)
        search_box.send_keys(target)
        time.sleep(2)
        
        print(f"[JARVIS]: Locating chat list entry for: '{target}'...")
        contact_xpath = (
            f'//div[@data-testid="cell-frame-title"]//*[translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="{target.lower()}"] | '
            f'//div[@data-testid="cell-frame-title" and translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="{target.lower()}"]'
        )
        try:
            contact_element = wait.until(EC.element_to_be_clickable((By.XPATH, contact_xpath)))
            contact_element.click()
        except Exception:
            try:
                fallback_xpath = f'//span[@title="{target}"] | //span[contains(@title, "{target}")] | //*[contains(text(), "{target}")]'
                contact_element = wait.until(EC.element_to_be_clickable((By.XPATH, fallback_xpath)))
                contact_element.click()
            except Exception:
                return f"Error: Could not locate contact '{target}' in WhatsApp search results."
        time.sleep(1)
        return "Success"

def whatsapp_login_session():
    driver = None
    try:
        print("\n[JARVIS]: Launching browser to scan WhatsApp QR code...")
        driver = get_shared_driver(headless=False)
        driver.get("https://web.whatsapp.com/")
        print("\n[JARVIS]: Please scan the QR code displayed on WhatsApp Web using your mobile phone.")
        print("[JARVIS]: Waiting up to 120 seconds for initialization...")
        
        start_time = time.time()
        logged_in = False
        while time.time() - start_time < 120:
            try:
                if not driver.window_handles:
                    return "Login cancelled: Browser window was closed by the user."
            except Exception:
                return "Login cancelled: Browser window was closed by the user."
                
            # Check for chat pane or search box (indicating logged in)
            if driver.find_elements(By.XPATH, '//div[@id="pane-side"] | //div[@data-testid="chat-list-search"]'):
                logged_in = True
                break
                
            time.sleep(1)
            
        if not logged_in:
            return "Login timed out: QR code was not scanned within 120 seconds."
            
        print("\n[JARVIS]: Login successful! Session has been saved.")
        time.sleep(3)
        return "Successfully authenticated WhatsApp session and saved state."
    except Exception as e:
        return f"Failed to log in: {e}"
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

def send_whatsapp_message(target, message):
    target = target.strip()
    message = message.strip()
    
    driver = None
    try:
        driver = get_shared_driver(headless=False)
        print("\n[JARVIS]: Initializing WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        try:
            logged_in = check_login_status(driver, timeout=15)
        except Exception as e:
            return f"Error: {e}"
            
        if logged_in is False:
            return "Error: WhatsApp is not logged in. Please run the 'whatsapp login' command first to scan your QR code."
        elif logged_in is None:
            return "Error: WhatsApp Web is taking too long to load. Please verify your internet connection and try again."
            
        wait = WebDriverWait(driver, 35)
        
        # Open chat
        res = open_chat_with_target(driver, wait, target)
        if res.startswith("Error"):
            return res
            
        # Wait for conversation chat bar
        print("[JARVIS]: Locating message input area...")
        msg_box_xpath = (
            '//div[@data-testid="conversation-compose-box-input"] | '
            '//div[@role="textbox" and @contenteditable="true" and contains(@data-testid, "compose")] | '
            '//div[@id="main"]//footer//div[@contenteditable="true"]'
        )
        msg_box = wait.until(EC.element_to_be_clickable((By.XPATH, msg_box_xpath)))
        
        print(f"[JARVIS]: Typing and sending message...")
        msg_box.send_keys(message)
        msg_box.send_keys(Keys.ENTER)
        time.sleep(2)
        return f"Successfully sent WhatsApp message to '{target}'."
            
    except Exception as e:
        return f"Failed to execute WhatsApp automation: {e}"

def whatsapp_send_file(target, filepath):
    if not os.path.exists(filepath):
        return f"Error: File not found at path: {filepath}"
    abs_path = os.path.abspath(filepath)
    
    driver = None
    try:
        driver = get_shared_driver(headless=False)
        print("\n[JARVIS]: Initializing WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        try:
            logged_in = check_login_status(driver, timeout=15)
        except Exception as e:
            return f"Error: {e}"
            
        if not logged_in:
            return "Error: WhatsApp is not logged in. Please run the 'whatsapp login' command first."
            
        wait = WebDriverWait(driver, 35)
        res = open_chat_with_target(driver, wait, target)
        if res.startswith("Error"):
            return res
            
        print(f"[JARVIS]: Uploading file: '{abs_path}'...")
        # Locate the file input in DOM
        file_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
        file_input.send_keys(abs_path)
        time.sleep(3) # Wait for preview modal to display
        
        print("[JARVIS]: Sending media...")
        
        # 1. First attempt: try pressing Enter on the active element (caption box)
        try:
            driver.switch_to.active_element.send_keys(Keys.ENTER)
            time.sleep(1.5)
        except Exception:
            pass
            
        # 2. Check if the preview screen is still open
        send_btn_xpath = '//*[@data-testid="send"] | //span[@data-icon="send"]/.. | //span[@data-icon="send"] | //button[@data-testid="compose-btn-send"] | //div[@role="button" and .//*[@data-icon="send"]]'
        candidates = driver.find_elements(By.XPATH, send_btn_xpath)
        still_open = any(el.is_displayed() for el in candidates if el)
        
        if still_open:
            print("[JARVIS]: Media preview still open. Executing button click strategies...")
            for el in candidates:
                try:
                    if el.is_displayed():
                        try:
                            el.click()
                            time.sleep(1.5)
                            break
                        except Exception:
                            driver.execute_script("arguments[0].click();", el)
                            time.sleep(1.5)
                            break
                except Exception:
                    pass
                    
        # 3. Final global fallback: if still open, send Enter key to body element
        candidates = driver.find_elements(By.XPATH, send_btn_xpath)
        still_open = any(el.is_displayed() for el in candidates if el)
        if still_open:
            print("[JARVIS]: Media preview still open. Sending global Enter key fallback...")
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
            except Exception:
                pass
                
        time.sleep(4) # Wait for send transfer
        return f"Successfully sent file '{os.path.basename(abs_path)}' to '{target}'."
    except Exception as e:
        return f"Failed to send file: {e}"

def whatsapp_list_unreads():
    driver = None
    try:
        driver = get_shared_driver(headless=False)
        print("\n[JARVIS]: Loading WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        try:
            logged_in = check_login_status(driver, timeout=15)
        except Exception as e:
            return f"Error: {e}"
            
        if not logged_in:
            return "Error: WhatsApp is not logged in. Please run the 'whatsapp login' command first."
            
        print("[JARVIS]: Scanning chat list for unread messages...")
        time.sleep(2)
        
        containers = driver.find_elements(By.XPATH, '//div[@data-testid="cell-frame-container"] | //div[contains(@data-testid, "list-item-")]')
        
        unreads = []
        for cell in containers:
            try:
                text = cell.text.strip()
                if "unread message" in text.lower():
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    unread_count = "1"
                    contact_name = "Unknown"
                    for line in lines:
                        if "unread message" in line:
                            unread_count = "".join(c for c in line if c.isdigit()) or "1"
                        elif line != unread_count and "unread message" not in line and ":" not in line and "/" not in line and line not in ["yesterday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                            contact_name = line
                    
                    titles = cell.find_elements(By.XPATH, './/div[@data-testid="cell-frame-title"] | .//span[@title]')
                    if titles:
                        contact_name = titles[0].text.strip() or titles[0].get_attribute("title") or contact_name
                        
                    unreads.append(f"  - {contact_name} ({unread_count} unread)")
            except Exception:
                pass
                
        if not unreads:
            return "You have no unread WhatsApp messages, sir."
            
        report = ["--- Unread WhatsApp Messages ---"] + unreads
        return "\n".join(report)
    except Exception as e:
        return f"Failed to list unreads: {e}"

def whatsapp_auto_reply_loop(reply_msg):
    global _auto_reply_active, _shared_driver
    print(f"\n[JARVIS]: Auto-reply responder thread launched with message: '{reply_msg}'")
    
    driver = None
    try:
        driver = get_shared_driver(headless=False)
        driver.get("https://web.whatsapp.com/")
        
        try:
            logged_in = check_login_status(driver, timeout=20)
        except Exception:
            logged_in = False
            
        if not logged_in:
            print("\n[JARVIS]: Auto-reply error: Browser is not logged in. Disabling responder.")
            _auto_reply_active = False
            return
            
        print("\n[JARVIS]: Auto-reply responder active and polling for new messages in background...")
        
        while _auto_reply_active:
            try:
                if not driver.window_handles:
                    print("\n[JARVIS]: Auto-reply disabled: Browser window was closed.")
                    _auto_reply_active = False
                    break
            except Exception:
                print("\n[JARVIS]: Auto-reply disabled: Browser window was closed.")
                _auto_reply_active = False
                break
                
            try:
                containers = driver.find_elements(By.XPATH, '//div[@data-testid="cell-frame-container"] | //div[contains(@data-testid, "list-item-")]')
                for cell in containers:
                    text = cell.text.strip()
                    if "unread message" in text.lower():
                        cell.click()
                        time.sleep(2)
                        
                        msg_box_xpath = (
                            '//div[@data-testid="conversation-compose-box-input"] | '
                            '//div[@role="textbox" and @contenteditable="true" and contains(@data-testid, "compose")] | '
                            '//div[@id="main"]//footer//div[@contenteditable="true"]'
                        )
                        msg_box = driver.find_element(By.XPATH, msg_box_xpath)
                        msg_box.send_keys(reply_msg)
                        msg_box.send_keys(Keys.ENTER)
                        print(f"\n[JARVIS]: Auto-replied to unread message.")
                        time.sleep(1)
            except Exception:
                pass
                
            time.sleep(8)
            
    except Exception as e:
        print(f"\n[JARVIS]: Auto-reply encountered an error: {e}")
    finally:
        _auto_reply_active = False

def whatsapp_read_last(target):
    driver = None
    try:
        driver = get_shared_driver(headless=False)
        print("\n[JARVIS]: Initializing WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        try:
            logged_in = check_login_status(driver, timeout=15)
        except Exception as e:
            return f"Error: {e}"
            
        if not logged_in:
            return "Error: WhatsApp is not logged in. Please run the 'whatsapp login' command first."
            
        wait = WebDriverWait(driver, 35)
        res = open_chat_with_target(driver, wait, target)
        if res.startswith("Error"):
            return res
            
        print("[JARVIS]: Scanning last incoming message...")
        time.sleep(1.5)
        
        bubbles = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in")]')
        if not bubbles:
            return f"There are no incoming messages in the chat with '{target}'."
            
        last_bubble = bubbles[-1]
        text_elements = last_bubble.find_elements(By.XPATH, './/span[contains(@class, "selectable-text")] | .//span')
        if text_elements:
            last_msg_text = text_elements[0].text.strip()
            return f"Last message from '{target}': \"{last_msg_text}\""
        return f"Could not extract the text content of the last message from '{target}'."
    except Exception as e:
        return f"Failed to read last message: {e}"

def whatsapp_get_status(target):
    driver = None
    try:
        driver = get_shared_driver(headless=False)
        print("\n[JARVIS]: Initializing WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        try:
            logged_in = check_login_status(driver, timeout=15)
        except Exception as e:
            return f"Error: {e}"
            
        if not logged_in:
            return "Error: WhatsApp is not logged in. Please run the 'whatsapp login' command first."
            
        wait = WebDriverWait(driver, 35)
        res = open_chat_with_target(driver, wait, target)
        if res.startswith("Error"):
            return res
            
        print("[JARVIS]: Inspecting status...")
        time.sleep(2)
        
        header = wait.until(EC.presence_of_element_located((By.XPATH, '//header[@data-testid="conversation-header"]')))
        sub_text_el = header.find_elements(By.XPATH, './/span[contains(text(), "online") or contains(text(), "typing")] | .//*[contains(@title, "online") or contains(@title, "typing")]')
        if sub_text_el:
            status_text = sub_text_el[0].text.strip() or sub_text_el[0].get_attribute("title") or "online"
            return f"Contact '{target}' is currently {status_text}."
        
        last_seen_el = header.find_elements(By.XPATH, './/span[contains(text(), "last seen") or contains(text(), "click here for contact info")]')
        if last_seen_el:
            txt = last_seen_el[0].text.strip()
            if "click here" in txt.lower():
                return f"Contact '{target}' status: Offline (Last seen details hidden/unavailable)."
            return f"Contact '{target}' status: {txt}."
            
        return f"Contact '{target}' is currently Offline."
    except Exception as e:
        return f"Failed to check status: {e}"

def whatsapp_trigger_call(target, call_type="voice"):
    driver = None
    try:
        driver = get_shared_driver(headless=False)
        print("\n[JARVIS]: Initializing WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        try:
            logged_in = check_login_status(driver, timeout=15)
        except Exception as e:
            return f"Error: {e}"
            
        if not logged_in:
            return "Error: WhatsApp is not logged in. Please run the 'whatsapp login' command first."
            
        wait = WebDriverWait(driver, 35)
        res = open_chat_with_target(driver, wait, target)
        if res.startswith("Error"):
            return res
            
        time.sleep(1.5)
        
        if call_type == "video":
            print(f"[JARVIS]: Triggering WhatsApp Video Call to '{target}'...")
            btn_xpath = '//div[@data-testid="video-call"] | //span[@data-icon="video-call"]/..'
        else:
            print(f"[JARVIS]: Triggering WhatsApp Voice Call to '{target}'...")
            btn_xpath = '//div[@data-testid="voice-call"] | //span[@data-icon="phone-call"]/.. | //span[@data-icon="phone"]/..'
            
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
        btn.click()
        time.sleep(2)
        return f"Successfully initiated WhatsApp {call_type} call to '{target}'."
    except Exception as e:
        return f"Failed to place WhatsApp call: {e}"

def whatsapp_broadcast(targets_list, message):
    driver = None
    try:
        driver = get_shared_driver(headless=False)
        print("\n[JARVIS]: Initializing WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        try:
            logged_in = check_login_status(driver, timeout=15)
        except Exception as e:
            return f"Error: {e}"
            
        if not logged_in:
            return "Error: WhatsApp is not logged in. Please run the 'whatsapp login' command first."
            
        wait = WebDriverWait(driver, 35)
        
        successful = []
        failed = []
        
        for raw_target in targets_list:
            target = raw_target.strip()
            if not target:
                continue
                
            print(f"\n[JARVIS]: Broadcasting message to: '{target}'...")
            res = open_chat_with_target(driver, wait, target)
            if res.startswith("Error"):
                failed.append(f"{target} ({res})")
                continue
                
            try:
                msg_box_xpath = (
                    '//div[@data-testid="conversation-compose-box-input"] | '
                    '//div[@role="textbox" and @contenteditable="true" and contains(@data-testid, "compose")] | '
                    '//div[@id="main"]//footer//div[@contenteditable="true"]'
                )
                msg_box = wait.until(EC.element_to_be_clickable((By.XPATH, msg_box_xpath)))
                msg_box.send_keys(message)
                msg_box.send_keys(Keys.ENTER)
                successful.append(target)
                time.sleep(2)
            except Exception as e:
                failed.append(f"{target} (Failed to send text: {e})")
                
        report = []
        if successful:
            report.append(f"Successfully broadcasted to: {', '.join(successful)}")
        if failed:
            report.append(f"Failed for targets: {'; '.join(failed)}")
        return "\n".join(report)
    except Exception as e:
        return f"Failed to execute broadcast: {e}"

def whatsapp_mute_chat(target, action="mute"):
    driver = None
    try:
        driver = get_shared_driver(headless=False)
        print("\n[JARVIS]: Initializing WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        try:
            logged_in = check_login_status(driver, timeout=15)
        except Exception as e:
            return f"Error: {e}"
            
        if not logged_in:
            return "Error: WhatsApp is not logged in. Please run the 'whatsapp login' command first."
            
        wait = WebDriverWait(driver, 35)
        res = open_chat_with_target(driver, wait, target)
        if res.startswith("Error"):
            return res
            
        time.sleep(1.5)
        
        print("[JARVIS]: Opening chat options menu...")
        menu_btn_xpath = '//div[@data-testid="conversation-menu-button"] | //header[@data-testid="conversation-header"]//span[@data-icon="menu"]/..'
        menu_btn = wait.until(EC.element_to_be_clickable((By.XPATH, menu_btn_xpath)))
        menu_btn.click()
        time.sleep(1)
        
        if action == "mute":
            print("[JARVIS]: Selecting mute action...")
            mute_option_xpath = '//div[text()="Mute notifications" or contains(text(), "Mute")]'
            mute_option = wait.until(EC.element_to_be_clickable((By.XPATH, mute_option_xpath)))
            mute_option.click()
            time.sleep(1)
            
            print("[JARVIS]: Muting indefinitely...")
            always_radio_xpath = '//label[contains(., "Always") or contains(., "always")] | //*[contains(text(), "Always")]/..'
            always_radio = wait.until(EC.element_to_be_clickable((By.XPATH, always_radio_xpath)))
            always_radio.click()
            time.sleep(0.5)
            
            confirm_btn_xpath = '//div[@role="button" and (text()="Mute notifications" or text()="Mute" or contains(text(), "Mute"))]'
            confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_btn_xpath)))
            confirm_btn.click()
            time.sleep(2)
            return f"Successfully muted chat notifications for '{target}' indefinitely."
        else:
            print("[JARVIS]: Selecting unmute action...")
            unmute_option_xpath = '//div[text()="Unmute notifications" or contains(text(), "Unmute")]'
            unmute_option = wait.until(EC.element_to_be_clickable((By.XPATH, unmute_option_xpath)))
            unmute_option.click()
            time.sleep(2)
            return f"Successfully unmuted chat notifications for '{target}'."
    except Exception as e:
        return f"Failed to modify chat mute status: {e}"

def whatsapp_logout_session():
    global _shared_driver
    driver = None
    try:
        driver = get_shared_driver(headless=False)
        print("\n[JARVIS]: Loading WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        try:
            logged_in = check_login_status(driver, timeout=10)
        except Exception:
            logged_in = False
            
        if not logged_in:
            try:
                driver.quit()
            except Exception:
                pass
            _shared_driver = None
            if os.path.exists(USER_DATA_DIR):
                import shutil
                try:
                    shutil.rmtree(USER_DATA_DIR)
                except Exception:
                    pass
            return "WhatsApp session was not logged in. Cleaned local profile cache successfully."
            
        wait = WebDriverWait(driver, 35)
        
        print("[JARVIS]: Opening main menu options...")
        menu_btn_xpath = '//div[@data-testid="menu"] | //span[@data-icon="menu"]/..'
        menu_btn = wait.until(EC.element_to_be_clickable((By.XPATH, menu_btn_xpath)))
        menu_btn.click()
        time.sleep(1)
        
        logout_option_xpath = '//div[text()="Log out" or contains(text(), "Log out")]'
        logout_option = wait.until(EC.element_to_be_clickable((By.XPATH, logout_option_xpath)))
        logout_option.click()
        time.sleep(1)
        
        confirm_btn_xpath = '//div[@role="button" and (text()="Log out" or text()="Log Out")]'
        confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_btn_xpath)))
        confirm_btn.click()
        time.sleep(5)
        
        try:
            driver.quit()
        except Exception:
            pass
        _shared_driver = None
        
        if os.path.exists(USER_DATA_DIR):
            import shutil
            try:
                shutil.rmtree(USER_DATA_DIR)
            except Exception:
                pass
                
        return "Successfully logged out of WhatsApp Web and cleared local session cache."
    except Exception as e:
        return f"Failed to complete logout: {e}"
