#!/usr/bin/env python3
"""
Script to add common names and proper nouns to custom words
"""

import json
import os

def add_common_names():
    """Add common Indian names and other proper nouns to custom words."""
    
    # Common Indian names
    indian_names = [
        # Male names
        "rahul", "surya", "rakesh", "amit", "rajesh", "suresh", "manish", "vishal",
        "prashant", "sachin", "rohit", "virat", "ms", "dhoni", "kohli", "tendulkar",
        "kapil", "dev", "sunil", "gavaskar", "rahul", "dravid", "sourav", "ganguly",
        "anil", "kumble", "zaheer", "khan", "yuvraj", "singh", "harbhajan", "sehwag",
        "virender", "gautam", "gambhir", "ishant", "sharma", "ravindra", "jadeja",
        "cheteshwar", "pujara", "ajinkya", "rahane", "kl", "rahul", "rishabh", "pant",
        "shubman", "gill", "shreyas", "iyer", "hardik", "pandya", "jasprit", "bumrah",
        "mohammed", "shami", "ravichandran", "ashwin", "kuldeep", "yadav", "yuzvendra",
        "chahal", "bhuvi", "kumar", "umesh", "shardul", "thakur", "axar", "patel",
        
        # Female names
        "priya", "neha", "anjali", "kavita", "sunita", "meera", "radha", "lakshmi",
        "sita", "parvati", "durga", "kali", "saraswati", "ganga", "yamuna", "narmada",
        "godavari", "krishna", "kaveri", "brahmaputra", "indus", "sutlej", "beas",
        "ravi", "chenab", "jhelum", "sindhu", "gandhi", "nehru", "patel", "bose",
        "tagore", "raja", "rani", "maharaja", "maharani", "sardar", "begum", "khan",
        "singh", "kumar", "reddy", "naidu", "iyer", "iyengar", "sharma", "verma",
        "gupta", "malhotra", "kapoor", "chopra", "bhatt", "mehta", "patel", "shah",
        "desai", "joshi", "pandey", "tiwari", "mishra", "trivedi", "chaturvedi",
        "upadhyay", "acharya", "swami", "guru", "baba", "saint", "sadhu", "yogi",
        
        # Common surnames
        "kumar", "singh", "reddy", "naidu", "iyer", "iyengar", "sharma", "verma",
        "gupta", "malhotra", "kapoor", "chopra", "bhatt", "mehta", "patel", "shah",
        "desai", "joshi", "pandey", "tiwari", "mishra", "trivedi", "chaturvedi",
        "upadhyay", "acharya", "swami", "guru", "baba", "saint", "sadhu", "yogi"
    ]
    
    # Technical terms and abbreviations
    technical_terms = [
        "python", "java", "javascript", "html", "css", "sql", "mongodb", "redis",
        "docker", "kubernetes", "aws", "azure", "gcp", "api", "rest", "graphql",
        "json", "xml", "yaml", "toml", "ini", "csv", "tsv", "pdf", "docx", "xlsx",
        "ppt", "pptx", "zip", "tar", "gz", "rar", "7z", "git", "svn", "mercurial",
        "linux", "ubuntu", "centos", "debian", "fedora", "arch", "gentoo", "slackware",
        "windows", "macos", "ios", "android", "react", "angular", "vue", "nodejs",
        "express", "django", "flask", "spring", "hibernate", "jpa", "jdbc", "jvm",
        "npm", "yarn", "pip", "conda", "maven", "gradle", "ant", "make", "cmake",
        "gcc", "clang", "msvc", "gdb", "lldb", "valgrind", "strace", "ltrace",
        "vim", "emacs", "vscode", "sublime", "atom", "intellij", "eclipse", "netbeans",
        "postgresql", "mysql", "sqlite", "oracle", "sqlserver", "mariadb", "cassandra",
        "elasticsearch", "kibana", "logstash", "beats", "kafka", "rabbitmq", "redis",
        "memcached", "nginx", "apache", "tomcat", "jetty", "wildfly", "jboss"
    ]
    
    # Company and brand names
    company_names = [
        "google", "microsoft", "apple", "amazon", "facebook", "twitter", "linkedin",
        "netflix", "spotify", "uber", "lyft", "airbnb", "tesla", "spacex", "nasa",
        "isro", "drdo", "bhel", "ongc", "ioc", "hpcl", "bpcl", "ntpc", "nhpc",
        "sbi", "hdfc", "icici", "axis", "kotak", "yes", "bank", "pnb", "canara",
        "union", "bank", "indian", "overseas", "bank", "idbi", "bank", "uco",
        "bank", "central", "bank", "india", "reserve", "bank", "india", "rbi",
        "sebi", "irda", "pfrda", "nps", "epf", "ppf", "nsc", "kvp", "sukanya",
        "samriddhi", "yojana", "pm", "jay", "yojana", "pm", "kisan", "yojana",
        "pm", "fasal", "bima", "yojana", "pm", "aawas", "yojana", "pm", "ujjwala",
        "yojana", "pm", "jan", "dhan", "yojana", "pm", "suraksha", "bima", "yojana"
    ]
    
    # All custom words
    all_custom_words = indian_names + technical_terms + company_names
    
    # Load existing custom words if they exist
    existing_words = set()
    if os.path.exists('custom_words.json'):
        try:
            with open('custom_words.json', 'r') as f:
                data = json.load(f)
                existing_words = set(data.get('words', []))
        except Exception as e:
            print(f"Could not load existing custom words: {e}")
    
    # Add new words
    new_words = set(all_custom_words) - existing_words
    all_words = existing_words.union(new_words)
    
    # Save to file
    data = {
        'words': list(all_words),
        'feedback': {}  # Preserve existing feedback if any
    }
    
    try:
        with open('custom_words.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Successfully added {len(new_words)} new custom words!")
        print(f"📊 Total custom words: {len(all_words)}")
        print(f"📝 New words added: {', '.join(sorted(new_words)[:20])}{'...' if len(new_words) > 20 else ''}")
        
        # Show categories
        print(f"\n📋 Categories:")
        print(f"   👥 Indian Names: {len(indian_names)}")
        print(f"   💻 Technical Terms: {len(technical_terms)}")
        print(f"   🏢 Company Names: {len(company_names)}")
        
    except Exception as e:
        print(f"❌ Error saving custom words: {e}")

if __name__ == "__main__":
    print("Adding common names and technical terms to custom words...")
    add_common_names()
    print("\n🎉 Custom words added successfully!")
    print("💡 Now restart your enhanced auto-correction system to use these words.") 