# views.py

import os
import json
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from django.shortcuts import render
from .forms import TickerFileUploadForm
from scripts.get10k import fetch_and_process_10k
from .ollama_interface import OllamaClient

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        return soup.get_text()

def generate_sankey_data(bucket_data):
    labels = list(bucket_data.keys())
    sources = []
    targets = []
    values = []
    for i, (source_label, value) in enumerate(bucket_data.items()):
        if value > 0:
            sources.append(0)  # Assume "Revenue" is at index 0
            targets.append(i)
            values.append(value)
    return labels, sources, targets, values

def index(request):
    if request.method == 'POST':
        form = TickerFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            ticker = form.cleaned_data.get('ticker')
            pdf_file = request.FILES.get('pdf_file')
            html_file = request.FILES.get('html_file')

            text_content = ""

            if pdf_file:
                with open('temp.pdf', 'wb+') as destination:
                    for chunk in pdf_file.chunks():
                        destination.write(chunk)
                text_content = extract_text_from_pdf('temp.pdf')
            elif html_file:
                with open('temp.html', 'wb+') as destination:
                    for chunk in html_file.chunks():
                        destination.write(chunk)
                text_content = extract_text_from_html('temp.html')
            elif ticker:
                text_content = fetch_and_process_10k(ticker)

            ollama_client = OllamaClient()
            prompt = f"""
You are an AI assistant analyzing a company's 10-K financial statement.

Instructions:
1. First, write a short readable financial summary for a human. Cover Revenue, Operating Costs, Net Income, and any other important observations.
2. After the summary, output a valid JSON block with financial categories and their numeric values.
Example format:
{{
  "Revenue": 123450000,
  "Operating Costs": 93210000,
  "Net Income": 29240000,
  "Innovation Investments": 10550000,
  "Administrative Expenses": 6850000,
  "Financial Items": 1230000,
  "Facility Maintenance": 1450000,
  "External Services": 5110000,
  "Compliance Costs": 3210000,
  "Marketing": 12340000,
  "Research and Development": 23110000,
 
}}
Rules:
- JSON must start immediately after the summary, no extra text.
- Use 0 if not found.
- Ensure valid JSON.

Data to analyze:
{text_content}
            """

            analysis = ollama_client.generate_response(prompt)

            try:
                split_index = analysis.index('{')
                story = analysis[:split_index].strip()
                json_data = analysis[split_index:]
                bucket_data = json.loads(json_data)
                sankey_labels, sankey_sources, sankey_targets, sankey_values = generate_sankey_data(bucket_data)
            except (ValueError, json.JSONDecodeError) as e:
                story = analysis
                sankey_labels, sankey_sources, sankey_targets, sankey_values = [], [], [], []

            return render(request, 'story/results.html', {
                'story': story,
                'sankey_labels': sankey_labels,
                'sankey_sources': sankey_sources,
                'sankey_targets': sankey_targets,
                'sankey_values': sankey_values
            })
    else:
        form = TickerFileUploadForm()
    return render(request, 'story/index.html', {'form': form})
