from flask import Flask, render_template, request, json
import requests
from celery import Celery





# noinspection PyBroadException
def compute_defference_in_attributes(old_data, new_data, difference_in_reccomendation_list):
    difference_in_reccomendation_list.append(set(old_data.keys()) - set(new_data.keys()))
    difference_in_reccomendation_list.append(set(new_data.keys()) - set(old_data.keys()))



def start_compare_recommendations_dictionary(old_dictionary, new_dictionary, result_to_show, recommandation_wise_result,
                                             attribute_difference_recommendation_wise,attribute_difference_recommendation_nested):
    # loop the dictionary
    for key_attr in old_dictionary:
        recommendation_list = []
        difference_in_reccomendation_list = []
        difference_in_reccomendation_list_nested = []
        recommandation_wise_result[key_attr] = recommendation_list
        attribute_difference_recommendation_wise[key_attr] = difference_in_reccomendation_list
        attribute_difference_recommendation_nested[key_attr] = difference_in_reccomendation_list_nested
        try:
            new_data = new_dictionary[key_attr]
        except Exception:
            add_data_to_result_to_show(recommendation_list, "Reccomendation not found in File 2 for key" + key_attr)
            continue
        old_data = old_dictionary[key_attr]
        compute_defference_in_attributes(old_data,new_data,difference_in_reccomendation_list)
        compare_recommendation(old_data, new_data, recommendation_list, key_attr,difference_in_reccomendation_list_nested)
        #write to file



def compare_recommendation(recommendation_old, recommendation_new, result_to_show, ket_attr,difference_in_reccomendation_list_nested):

    if elements_of_same_instance(recommendation_old, recommendation_new):

        if isinstance(recommendation_new, dict):
            compare_dict_value(recommendation_old,recommendation_new,result_to_show,ket_attr,"",difference_in_reccomendation_list_nested)
        elif isinstance(recommendation_new, (list, set)):

            compare_list_values(recommendation_old, recommendation_new, result_to_show, ket_attr, ""),difference_in_reccomendation_list_nested
        elif isinstance(recommendation_new, (str, int, float, bool,unicode)):

            compare_single_value(recommendation_old, recommendation_new, result_to_show, ket_attr, ket_attr,difference_in_reccomendation_list_nested)

    else:
        add_data_to_result_to_show(result_to_show, "Recommendation is not of same type insatance for key " + ket_attr)


def compare_single_value(recommendation_old, recommendation_new, result_to_show, ket_attr, current_attribute_name,difference_in_reccomendation_list_nested):
    if(isinstance(recommendation_new,(str,unicode))):
        recommendation_new = str(recommendation_new).strip().replace("AmadeusINMPTBV2","AmadeusIN").replace("SpicejetV2","Spicejet")
        recommendation_old.strip()

    if not recommendation_old == recommendation_new:
        #print "Value does not match"
        add_data_to_result_to_show(result_to_show,
                                   "Value does not match in Recommendation " + str(ket_attr) + " Attribute Name " +
                                   current_attribute_name+" with values :---- "+str(recommendation_old)+" -----  "+str(recommendation_new))


def compare_unknown_element(old_data, new_data, result_to_show, ket_attr, current_attribute_name,difference_in_reccomendation_list_nested):
    if elements_of_same_instance(old_data, new_data):
        #print "start comparing"

        if isinstance(old_data, dict):
            #print "start dic comparision"
            compare_dict_value(old_data,new_data,result_to_show,ket_attr,current_attribute_name,difference_in_reccomendation_list_nested)
        elif isinstance(old_data, (list, set)):
            #print "comapre list or set"
            compare_list_values(old_data, new_data, result_to_show, ket_attr, current_attribute_name,difference_in_reccomendation_list_nested)
        elif isinstance(old_data, (str, int, float, bool,unicode)):
            #print "Compare single value"
            compare_single_value(old_data, new_data, result_to_show, ket_attr, current_attribute_name,difference_in_reccomendation_list_nested)
    else:
        add_data_to_result_to_show(result_to_show, "Recommendation is not of same type insatance for key " + ket_attr)


def compare_list_values(list_one, list_two, result_to_show, ket_attr, current_attribute_name,difference_in_reccomendation_list_nested):
    #print "start comparing list"
    if not len(list_one) == len(list_two):
        add_data_to_result_to_show(result_to_show,
                                   "Length of List found is not equal for Recommendation " + ket_attr +
                                   " Attribute Name " + current_attribute_name+" value 1 ----"+str(list_one)+"   ----value 2 -------"+str(list_two))
        add_data_to_result_to_show(difference_in_reccomendation_list_nested,"Length of List found is not equal for Recommendation " + ket_attr +
                                   " Attribute Name " + current_attribute_name+" value 1 ----"+str(list_one)+"   ----value 2 -------"+str(list_two))
    else:
        counter = 0
        list_one.sort()
        list_two.sort()
        for old_data in list_one:
            compare_unknown_element(old_data, list_two[counter], result_to_show, ket_attr,
                                    current_attribute_name + ":" + str(counter),difference_in_reccomendation_list_nested)
            counter=counter+1


def compare_dict_value(dict_old, dict_new, result_to_show, ket_attr, current_attribute_name,difference_in_reccomendation_list_nested):
    #print "Comparing dictionary value"
    for attribute in dict_old:
        try:
            new_value = dict_new[attribute]
        except:
            add_data_to_result_to_show(result_to_show, "Element not found for Recommendation with key " + ket_attr
                                       + " attribute " + current_attribute_name + attribute)
            add_data_to_result_to_show(difference_in_reccomendation_list_nested, "Element not found for Recommendation with key " + ket_attr
                                       + " attribute " + current_attribute_name + attribute)
        old_value = dict_old[attribute]
        compare_unknown_element(old_value, new_value, result_to_show, ket_attr,current_attribute_name + "." + attribute,difference_in_reccomendation_list_nested)



def file_from_url(url):

    try:
        u_response = requests.get(url)
    except requests.ConnectionError:
        return "Connection Error"
    data = json.loads(u_response.text)
    return data

def load_file_from_upload(file):
    try:
        data = file.read()
    except:
        return "Connection Error"
    data = json.loads(data)
    return data




def add_data_to_result_to_show(result_to_show, param):
    #print "adding value to result to show"
    result_to_show.insert(len(result_to_show), str(param))


def scoop_json(data, index_of_data, attrs):

    if isinstance(data,dict):
        attrs = attrs.split(".")
        for att in attrs:
            data = data[att]
        return data
    else:
        if len(attrs) > 0:
            attrs = attrs.split(".")
            data = data[int(index_of_data)]
            for att in attrs:
                data = data[att]
            return data
        else:
            return data


def convert_list_to_dic_and_filter(data, key_attr, appender, service):

    dictionary = {}
    for value in data:
        if len(service) > 0:
            if (value[key_attr].lower()).find(service.lower()) != -1:
                key = generate_key(value[key_attr], appender)
                dictionary[key] = value
        else:
            key = generate_key(value[key_attr], appender)
            dictionary[key] = value

    return dictionary


def generate_key(value, appender):
    if appender == 'REM_AFTER_LAST_UNDERSCORE':
        value = value[0:value.rindex("_")]
        return value.lower()
    if appender == 'NOTHING':
        return value.lower()


def elements_of_same_instance(element_1, element_2):
    if type(element_1) == type(element_2):
        return True
    else:
        return False




