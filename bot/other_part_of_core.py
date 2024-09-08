import protocol_formater

def create_protocol(output_name: str, params: dict):
    if params["formal"]:
        json_path = "official_answer.json"
        protocol_formater.create_formal_docx(json_path, output_name + ".docx",
                            params["timecodes"], params["discussion_context"],params["list_of_orders"])
        protocol_formater.create_formal_pdf(json_path, output_name + ".pdf",
                            params["timecodes"], params["discussion_context"],params["list_of_orders"])
        print("Done.")
    else:
        json_path = "unofficial_answer.json"
        protocol_formater.create_informal_docx(json_path, output_name + ".docx", params["timecodes"])
        protocol_formater.create_informal_pdf(json_path, output_name + ".pdf", params["timecodes"])
        print("Done.")
