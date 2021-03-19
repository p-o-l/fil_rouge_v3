"""
Route functions for the fil_rouge_v0.3 flask app
"""
# Standard library imports
import os
import io

# Related third party imports:
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import flask_restful
from PIL import Image
import uuid
import base64
import json
import sys
import csv
import PyPDF2

# AWS imports:
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

# Imports specific to the application:
import my_flask_package


# ########## GLOBAL CONSTANTS #############
ENCODING = 'utf-8'
# ENCODING = 'ascii'
S3_BUCKET_NAME ='fil-rouge-v0.3-bucket'
MAX_REKOGNITION_LABEL_COUNT = 10


# ########## API UPLOAD FILE ROUTE #############
@my_flask_package.app.route("/send_file/", methods=["POST"])
def recieve_file_from_client():
    """ Receives a file from a client and returns it as a JSON stream, along with meta-data
    - Renames the file with a UID, keeping the existing extension
    - check if the file is not empty and if the extension is an accepted format
    - accepted formats: .jpg, .png, .gif, .txt, .pdf, .csv
    --- limitations: 
    -----Does not do additional security checks (max length for example, or is the .jpg file really a .jpg image)
    -----only accepts one file at a time
    
    :param nil
    :rtype : json

    :Example
    >>> r = requests.post('http://127.0.0.1:5000/send_image/', files={'image': open('test.jpg', 'rb')})
    {'image id': 'cd133cad-4cc2-11eb-afcd-408d5c0b3636.jpg', 'msg': 'success', 'size': [1600, 1064]...}
    """
    
    # get the file posted by the client
    file = request.files['file']


    # abort if no file sent:
    if not file:
        flask_restful.abort(404, message="No file was received. Try again with a real file")  # 404 could not find resource
            
    # check that there is a file when submit is pressed 
    if file.filename != '':  

        extension = os.path.splitext(file.filename)[1]
        
        # get generic metadata
        file_content_type = file.content_type
        file_mimetype = file.mimetype
        
        # reject invalid file extensions file extensions
        if extension not in my_flask_package.app.config['UPLOAD_EXTENSIONS']:
            response = jsonify({'msg': 'failure', 'reason': 'un-supported file type'}), 415
        
        else:
            #print("\n test test test \n")
            #print("test2")
            # generate a filename with a UUID for the image
            filename_with_uuid = str(uuid.uuid1()) + extension
            
            # ########## HANDLE TXT FILES #############
            if extension == '.txt':
                text_file = file.read()
                #with open (file, 'r') as text:
                #    print(type(text), text)
                decoded_text_file = text_file.decode("utf-8")
                
                num_chars = len(decoded_text_file)
                words = decoded_text_file.split()
                num_words = len(words)
                num_lines = decoded_text_file.count('\n') + 1
                   
                # print("\n", num_chars, "chars, ", num_words, "words, ", num_lines, "lines\n")
                
                metadata = {'msg': 'success', 'type': extension, 'num chars': num_chars, 'num_words': num_words, 'num lines': num_lines, 'content type': file_content_type }

                response = jsonify({'data': decoded_text_file, 'metadata': metadata}), 200
                
                #response = jsonify({'msg': 'success', 'type': extension, 'num chars': num_chars, 'num_words': num_words, 'num lines': num_lines, 'data': decoded_text_file}), 200

            # ########## HANDLE CSV FILES #############
            elif extension == '.csv':
                csv_file = file.read()
                decoded_csv_file = csv_file.decode("utf-8")
                
                # count the number of columns
                first_line = ''
                #for char in decoded_csv_file:
                #    while char != "\":
                #        first_line += char
                #num_columns = first_line.count(',') + 1   
                
                num_lines = decoded_csv_file.count('\n') + 1
                
                # print(decoded_csv_file)
                csv_dicts = [{k: v for k, v in row.items()} for row in csv.DictReader(decoded_csv_file.splitlines(), skipinitialspace=True)]
                number_columns = len(csv_dicts[0])

                metadata = {'msg': 'success', 'file id': filename_with_uuid, 'type': extension, 'num columns': number_columns, 'num lines': num_lines, 'content type': file_content_type}
                
                response = jsonify({'data': csv_dicts, 'metadata': metadata}), 200

                #response = jsonify({'msg': 'success', 'type': extension, 'num columns': number_columns, 'num lines': num_lines, 'data': csv_dicts}), 200
            
            # ########## HANDLE PDF FILES #############
            elif extension == '.pdf':
                # print("file type", type(file))
                pdf_file = file.read()
                # print("pdf read type", type(pdf_file))

                # get the text and metadata from the file
                with io.BytesIO(pdf_file) as open_pdf_file:
                    read_pdf = PyPDF2.PdfFileReader(open_pdf_file)
                    num_pages = read_pdf.getNumPages()
                    pdf_doc_info = read_pdf.getDocumentInfo()
                    
                    # extract the text in each page, and add it to a text string
                    text_so_far = ""
                    for page_num in range(num_pages):
                        raw_text_of_current_page = read_pdf.getPage(page_num).extractText()
                        text_so_far += raw_text_of_current_page
                    # print("\n text so far", text_so_far)
                
                    # base64_encoded_pdf = base64.b64encode(open_pdf_file.read())
                    # base64_encoded_pdf = base64.b64encode(pdf_file.read())
                base64_encoded_data = base64.b64encode(pdf_file)
                base64_pdf_string = base64_encoded_data.decode(ENCODING)
                
                # encode the pdf into bytes64 format
                # with open("book.pdf", "rb") as pdf_file:
                #     base64_encoded_pdf = base64.b64encode(pdf_file.read())
                
                # img = Image.open(file.stream)
            
                # in_mem_file = io.BytesIO() 
                # img.save(in_mem_file, format = "PNG")
                # in_mem_file.seek(0)
                # img_bytes = in_mem_file.read()

                # base64_encoded_result_bytes = base64.b64encode(img_bytes)
                # base64_encoded_result_str = base64_encoded_result_bytes.decode(ENCODING)
                
                # 'document as bytes': open_pdf_file
                # response = jsonify(indent=2, sort_keys=False, result="This is just a test")
                
                metadata = {'msg': 'success', 'file id': filename_with_uuid, 'num pages': num_pages, 'document information': pdf_doc_info, 'content type': file_content_type}
                
                response = jsonify({'file encoded into base64': base64_pdf_string, 'text': text_so_far, 'metadata': metadata}), 200
                #response = jsonify({'msg': 'success', , 'text': text_so_far, 'file encoded into base64': base64_pdf_string}), 200


            # ########## HANDLE IMAGES #############
            else:
                # Read the image into memory using Pillow, via file.stream
                img = Image.open(file.stream)
            
                in_mem_file = io.BytesIO()

                img.save(in_mem_file, format = "PNG")
                image_bytes_size = in_mem_file.tell()
                
                # reset file pointer to start
                in_mem_file.seek(0)
                
                img_bytes = in_mem_file.read()

                base64_encoded_result_bytes = base64.b64encode(img_bytes)
                base64_encoded_result_str = base64_encoded_result_bytes.decode(ENCODING)
            
                # first: reading the binary stuff
                # note the 'rb' flag
                # result: bytes
                #with open(img, 'rb') as open_file:
                #    byte_content = open_file.read()
                
                # encode the image into base64
                #base64_bytes = base64.b64encode(byte_content)
                
                # third: decode these bytes to text
                # base64_string = base64.base64_bytes.decode(ENCODING)

                # optional: doing stuff with the data
                # raw_data = {"file_name_to_insert_here": base64_encoded_result_str}

                # now: encoding the data to json
                # json_data = json.dumps(raw_data, indent=4)
                
                # save the image using the UID
                # img.save(os.path.join(my_flask_package.app.config['UPLOAD_PATH'], filename_with_uuid))
               
                # (optional) test code to save the return stream to a file, in case your shell runs out of memory (for large images)
                # with open("return_stream_as_file.txt", 'w') as test_file_to_store_return_stream:
                #    test_file_to_store_return_stream.write(str({'msg': 'success', 'size': [img.width, img.height], 'image id': filename_with_uuid, 'json_file': raw_data}))
                
                
                # ########## IMAGE AWS REKOGNITION CODE  #############
                rekognition_labels = {}

                try:
                    session = boto3.Session(profile_name = 'csloginstudent')
                    rekogition_client = session.client('rekognition')
               
                    rekognition_response = rekogition_client.detect_labels(Image={'Bytes': img_bytes}, MaxLabels=MAX_REKOGNITION_LABEL_COUNT)
                        
                    for label in rekognition_response['Labels']:
                        rekognition_labels[label['Name']] = round(label['Confidence'], 2)

                except ProfileNotFound:
                    rekognition_labels = None

                # ########## IMAGE OUTPUTS #############
                metadata = {'msg': 'success', 'size': [img.width, img.height], 'image id': filename_with_uuid, 'aws-rekognition-response': rekognition_labels, 'content type': file_content_type, 'mimetype': file_mimetype, 'bytes size': image_bytes_size}
                
                response = jsonify({'json_file': base64_encoded_result_str, 'metadata': metadata}), 200
                
            # ########## UPLOAD FILE TO S3 #############
            # upload file from EC2 HD to S3 (deprecated - not working) #
            # file_save_path = SAVE_FOLDER_PATH + filename_with_uuid
            # file.save(file_save_path)
            # s3 = boto3.resource('s3')
            # s3.meta.client.upload_file('test.txt', S3_BUCKET_NAME, filename_with_uuid)
            # s3.meta.client.upload_file(file_save_path, S3_BUCKET_NAME, filename_with_uuid)
            # os.remove(file_save_path)

            # alternative way of uploading a file from EC2 HD to S3 (deprecated)
            #session = boto3.Session(profile_name = 'csloginstudent')
            #s3_client = session.client('s3')
            #s3_client.upload_file(Filename = 'test.txt', Bucket = S3_BUCKET_NAME, Key = 'test.txt')
            
            # save an in-memory text file
            # this method has a major problem with on-and-off upstream errors linked to NGINX.
            if extension == '.txt':
                s3 = boto3.resource('s3')
                s3.Bucket(S3_BUCKET_NAME).put_object(Key=filename_with_uuid, Body=text_file)

    return response
