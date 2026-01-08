###
# This file is not meant ot be executed directly.
# It is an example script showing how to execute the prompt1v2 templates


./do_query_llm_gpu 0 Fedora gpt4all.Meta-Llama-3-8B-Instruct.Q4_0 \
    --base_package_list "./csv/dnf-packages-with-desc-depend-prompt1v2.csv" \
    --template_alternative prompt1v2 \
    --custom_attributes "package,cryptographic_relevance,justification"

./do_query_llm_gpu 1 Fedora gpt4all.Nous-Hermes-2-Mistral-7B-DPO.Q4_0 \
    --base_package_list "./csv/dnf-packages-with-desc-depend-prompt1v2.csv" \
    --template_alternative prompt1v2 \
    --custom_attributes "package,cryptographic_relevance,justification"

./do_query_llm_gpu 2 Fedora gpt4all.Phi-3-mini-4k-instruct.Q4_0 \
    --base_package_list "./csv/dnf-packages-with-desc-depend-prompt1v2.csv" \
    --template_alternative prompt1v2 \
    --custom_attributes "package,cryptographic_relevance,justification"

./do_query_llm_gpu 3 Fedora gpt4all.gpt4all-13b-snoozy-q4_0 \
    --base_package_list "./csv/dnf-packages-with-desc-depend-prompt1v2.csv" \
    --template_alternative prompt1v2 \
    --custom_attributes "package,cryptographic_relevance,justification"

./do_query_llm_gpu 4 Fedora ollama.deepseek-r1:latest \
    --base_package_list "./csv/dnf-packages-with-desc-depend-prompt1v2.csv" \
    --template_alternative prompt1v2 \
    --custom_attributes "package,cryptographic_relevance,justification" \
    --host "https://olama-host.de:11434/"


./do_query_llm_no_gpu Fedora openai.gpt-5 \
    --base_package_list "./csv/dnf-packages-with-desc-depend-prompt1v2.csv" \
    --template_alternative prompt1v2 \
    --custom_attributes "package,cryptographic_relevance,justification" \
    --api_key "$OPENAI_API_KEY"
    --query-restriction 1

./do_query_llm_no_gpu Fedora openai.gpt-5 \
    --base_package_list "./csv/dnf-packages-with-desc-depend-prompt1v2.csv" \
    --template_alternative prompt1v2 \
    --custom_attributes "package,cryptographic_relevance,justification" \
    --api_key "$OPENAI_API_KEY" \
    --query_restriction 1

./do_query_llm_no_gpu Fedora gemini.gemini-2.5-flash \
    --base_package_list "./csv/dnf-packages-with-desc-depend-prompt1v2.csv" \
    --template_alternative prompt1v2 \
    --custom_attributes "package,cryptographic_relevance,justification" \
    --api_key "$GEMINI_API_KEY" \
    --query_restriction 1

./do_query_llm_no_gpu Fedora gemini.gemini-2.5-pro \
    --base_package_list "./csv/dnf-packages-with-desc-depend-prompt1v2.csv" \
    --template_alternative prompt1v2 \
    --custom_attributes "package,cryptographic_relevance,justification" \
    --api_key "$GEMINI_API_KEY" \
    --query_restriction 1

./do_query_llm_no_gpu Fedora mistral.codestral-2508 \
    --base_package_list "./csv/dnf-packages-with-desc-depend-prompt1v2.csv" \
    --template_alternative prompt1v2 \
    --custom_attributes "package,cryptographic_relevance,justification" \
    --api_key "$MISTRAL_API_KEY" \
    --query_restriction 1
