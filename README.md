# ☁️ Mukesh Kumar — Student Developer Portfolio
### Official Submission for the AWS Student Portfolio Hackathon 2026

![AWS Amplify](https://img.shields.io/badge/AWS-Amplify_Hosting-FF9900?logo=awsamplify&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-5_Skill_Badges-4285F4?logo=googlecloud&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-itsrockmukesh-181717?logo=github&logoColor=white)
![Education](https://img.shields.io/badge/Mirai_School_of_Tech-1st_Year_BE--CSE-3B82F6)
![License](https://img.shields.io/badge/License-MIT-10B981)

---

## 📌 1. Project Description
This portfolio website is designed and developed by **Mukesh Kumar**, a 1st-year **Bachelor of Engineering in Computer Science (BE-CSE)** student at **Mirai School of Technology**, for the **AWS Student Portfolio Hackathon 2026**.

The portfolio reflects Mukesh's authentic learning journey:
- Constructing solid foundations in **Web Development** using clean **HTML5 and CSS3**.
- Solving **Data Structures and Algorithms (DSA)** in **C++**.
- Earning **5 Google Cloud Skill Badges** in Compute, IAM, Data, and Generative AI prototyping.
- Delivering a production-grade, responsive developer portfolio with an embedded **Secret Developer Terminal** hosted on **AWS Amplify Hosting**.

---

## 💻 2. Technologies Used

| Category | Technologies |
|---|---|
| **Education & Profile** | 1st Year BE-CSE @ Mirai School of Technology |
| **Frontend Foundation** | Semantic HTML5, Vanilla Modern CSS3, Modular ES6+ JavaScript |
| **Core Programming** | C++ (Data Structures & Algorithms, STL, Problem Solving) |
| **Cloud Hosting** | **AWS Amplify Hosting**, Amazon CloudFront Global Edge CDN, SSL/HTTPS |
| **Creative Feature** | Embedded Retro Developer Terminal, Web Audio API Sound Synthesizer, HTML5 Canvas Constellation |
| **Version Control** | Git & GitHub ([@itsrockmukesh](https://github.com/itsrockmukesh)) |

---

## ⚡ 3. Creative Interactive Feature — Secret Developer Terminal

The portfolio includes an interactive **Retro/Cyber Developer Console** that runs directly in the browser.

### How to Open:
- **Keyboard Shortcut:** Press **`~`** (tilde) or **`` ` ``** (backtick) anywhere on the page.
- **Floating Badge:** Click the glowing badge in the bottom-right corner (*"✨ Curious? Try the secret terminal — press `~` or click here!"*).
- **Navigation & Hero:** Click the **`>_ Terminal`** button in the header or **`>_ Launch Terminal`** in the Hero section.

### Available Commands:
- **`help`**: Displays the full command list.
- **`about`**: Explains Mukesh's journey as a 1st-year BE-CSE student at Mirai School of Technology.
- **`skills`**: Formatted ASCII proficiency bars covering HTML/CSS, C++ DSA, and Cloud.
- **`projects`**: Lists Mukesh's projects on GitHub with direct links (`Personal-Website`, `Wikipedia`, `portfolio`).
- **`achievements`**: Details the 5 verified Google Cloud Skill Badges.
- **`contact`**: Outputs direct communication channels and GitHub links.
- **`funfact`**: Randomizes trivia about Mukesh's college journey and coding.
- **`aws`**: Explains the AWS Amplify Hosting and Amazon CloudFront CDN architecture.
- **`theme`**: Cycles terminal color themes (*Matrix Green*, *Synthwave Purple*, *Cyan Ocean*).
- **`clear`** / **`exit`**: Cleans the screen or smoothly closes the terminal.
- **Arrow Keys & Tab Autocomplete:** Press **Up/Down** for command history and **Tab** for auto-completion.
- **Web Audio API Synth:** Generates instant cyber sound feedback without external audio files.

---

## 📂 4. Featured Projects on GitHub

1. **[Personal-Website](https://github.com/itsrockmukesh/Personal-Website)**
   - *Tech:* HTML5, CSS3, Responsive Design
   - *Description:* Elegant personal developer webpage showcasing profile and skills.
2. **[Wikipedia Web Recreation](https://github.com/itsrockmukesh/Wikipedia)**
   - *Tech:* Semantic HTML5, Structured Content Hierarchy
   - *Description:* Clean recreation of the Wikipedia encyclopedic layout.
3. **[DevTerminal Portfolio](https://github.com/itsrockmukesh)**
   - *Tech:* AWS Amplify Hosting, HTML5/CSS3, Web Audio API, JavaScript CLI
   - *Description:* Flagship project for the AWS Student Portfolio Hackathon with secret terminal.
4. **C++ Data Structures & Algorithms Lab**
   - *Tech:* C++20, STL, Arrays, Trees, Recursion, Time Complexity
   - *Description:* Core algorithmic problem solving and optimized data structure implementations.

---

## 🏆 5. Verified Google Cloud Skill Badges

1. **The Basics of Google Cloud Compute** — Provisioning Compute Engine VMs, persistent disks, and network rules.
2. **Configure Service Accounts and IAM Roles for Google Cloud** — Least-privilege access, custom IAM roles, and credential key security.
3. **Store, Process, and Manage Data on Google Cloud – Console** — Cloud Storage buckets, BigQuery analytics, and database management.
4. **Develop AI-Powered Prototypes in Google AI Studio** — Multi-turn prompts, system instructions, and parameter tuning.
5. **Create Your First Gemini Enterprise Application** — Enterprise multimodal endpoints and production web application deployment.

---

## ☁️ 6. AWS Amplify Hosting Deployment Architecture

```
                    ┌─────────────────────────────────────────┐
                    │               GitHub Repo               │
                    │        (itsrockmukesh/portfolio)        │
                    └────────────────────┬────────────────────┘
                                         │ Git Push (main)
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │           AWS Amplify Hosting           │
                    │       Continuous CI/CD Build & Run      │
                    └────────────────────┬────────────────────┘
                                         │ Automated Distribution
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │         Amazon CloudFront (CDN)         │
                    │      Global Edge Caching & SSL TLS      │
                    └────────────────────┬────────────────────┘
                                         │ Sub-second Load Speed
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │            End-User Browser             │
                    │        (Desktop, Tablet, Mobile)        │
                    └─────────────────────────────────────────┘
```

---

## 🚀 7. Step-by-Step Deployment Instructions

### Step 1: Push Local Code to GitHub
```bash
# Push to your GitHub account (itsrockmukesh)
git add .
git commit -m "feat: complete AWS hackathon rubric alignment, superpowers section, and submission documentation"
git remote add origin https://github.com/itsrockmukesh/portfolio.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on AWS Amplify Hosting
1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/).
2. Click **"Deploy an app"** or **"Host web app"**.
3. Select **GitHub** and authenticate your account (`@itsrockmukesh`).
4. Select the repository and `main` branch.
5. AWS Amplify will detect [`amplify.yml`](amplify.yml) automatically.
6. Click **"Save and deploy"**.
7. In ~30 seconds, your portfolio will be live with a free SSL certificate!

---

## 📬 8. Contact & Socials
- **Student:** Mukesh Kumar
- **College:** Mirai School of Technology (1st Year BE-CSE)
- **GitHub:** [https://github.com/itsrockmukesh](https://github.com/itsrockmukesh)
- **Email:** techmukesh3124@gmail.com
- **LinkedIn:** [https://www.linkedin.com/in/mukesh-kumar-06485222a](https://www.linkedin.com/in/mukesh-kumar-06485222a)

---
*Created for the AWS Student Portfolio Hackathon 2026.*
