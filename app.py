from flask import Flask , render_template, request
from datetime import date , datetime

from helpme import file_from_url , load_file_from_upload,elements_of_same_instance,add_data_to_result_to_show,compare_dict_value,compare_list_values,compare_recommendation,compare_single_value,\
    compare_unknown_element,compute_defference_in_attributes,convert_list_to_dic_and_filter,generate_key,scoop_json,start_compare_recommendations_dictionary

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/searchcomparebatch',methods=['POST'])
def batch_search_comparator():

    data = load_file_from_upload(request.files['batch'])
    url1 = data['host1']+'/international/json/listing/'+data['lob1']
    url2 = data['host2']+'/international/json/listing/'+data['lob2']
    case_wise_result_to_show = {}
    case_wise_recommandation_wise_result = {}
    case_wise_attribute_difference_recommendation_wise = {}
    attribute_difference_recommendation_nested = {}
    for case in data['cases']:
        case_string = "/"+case['trip']+"/"+case['date']+"/"+case['pax']+"/"+case['lastval']
        old_url = url1+case_string
        new_url = url2+case_string

        result_to_show = []
        recommandation_wise_result = {}
        attribute_difference_recommendation_wise = {}
        attribute_difference_recommendation_wise_nested = {}
        case_wise_result_to_show[case_string] = result_to_show
        case_wise_recommandation_wise_result[case_string]= recommandation_wise_result
        case_wise_attribute_difference_recommendation_wise[case_string] = attribute_difference_recommendation_wise
        attribute_difference_recommendation_nested[case_string] = attribute_difference_recommendation_wise_nested

        # load Files From Url
        old_json = file_from_url(old_url)
        new_json = file_from_url(new_url)
        if old_json == "Connection Error":
            add_data_to_result_to_show(result_to_show, "Error while uploading File 1")
            continue
            #return render_template('result.html', data=result_to_show,data2 = recommandation_wise_result,data3 = attribute_difference_recommendation_wise)
        if new_json == "Connection Error":
            add_data_to_result_to_show(result_to_show, "Error while uploading File 2")
            continue
            #return render_template('result.html', data=result_to_show,data2 = recommandation_wise_result,data3 = attribute_difference_recommendation_wise)

        old_json = scoop_json(old_json, 0, "results")
        new_json = scoop_json(new_json, 0, "results")

        add_data_to_result_to_show(result_to_show, 'Length of results in File 1 without filter ' + str(len(old_json)))
        add_data_to_result_to_show(result_to_show, 'Length of results in File 2 without filter ' + str(len(new_json)))

        # create dictionary and filter according to airline
        services = request.form['service']
        old_dictionary = convert_list_to_dic_and_filter(old_json, request.form['dictionary_id_1'],
                                                    "REM_AFTER_LAST_UNDERSCORE", services)
        new_dictionary = convert_list_to_dic_and_filter(new_json, request.form['dictionary_id_2'],
                                                    "REM_AFTER_LAST_UNDERSCORE", services)

        old_json = None
        new_json = None

        add_data_to_result_to_show(result_to_show, 'Length of results in File 1 after filter ' + str(len(old_dictionary)))
        add_data_to_result_to_show(result_to_show, 'Length of results in File 2 after filter ' + str(len(new_dictionary)))


        if not isinstance(old_dictionary, dict):
            add_data_to_result_to_show(result_to_show, "Unable to convert dictionary for file 1 , Internal Error")
            continue
            #return render_template("result.html", data=result_to_show,data2 = recommandation_wise_result,data3=attribute_difference_recommendation_wise)
        if not isinstance(new_dictionary, dict):
            add_data_to_result_to_show(result_to_show, "Unable to convert dictionary for file 2 , Internal Error")
            continue
            #return render_template("result.html", data=result_to_show,data2 = recommandation_wise_result,data3=attribute_difference_recommendation_wise)

        start_compare_recommendations_dictionary(old_dictionary, new_dictionary, result_to_show, recommandation_wise_result,attribute_difference_recommendation_wise,attribute_difference_recommendation_wise_nested)


    return render_template('result.html', data=case_wise_result_to_show,data2 = case_wise_recommandation_wise_result,
                           data3 = case_wise_attribute_difference_recommendation_wise,data4 = attribute_difference_recommendation_nested)



@app.route('/searchcompare',methods=['POST'])
def search_comparator():

    result_to_show = []
    recommandation_wise_result = {}
    attribute_difference_recommendation_wise_level1 = {}
    attribute_difference_recommendation_nested = {}

    # load Files From Url
    old_json = file_from_url(request.form['old_url'])
    new_json = file_from_url(request.form['new_url'])
    if old_json == "Connection Error":
        add_data_to_result_to_show(result_to_show, "Error while uploading File 1")
        return render_template('singleresult.html', data=result_to_show,data2 = recommandation_wise_result,data3 = attribute_difference_recommendation_wise_level1)
    if new_json == "Connection Error":
        add_data_to_result_to_show(result_to_show, "Error while uploading File 2")
        return render_template('singleresult.html', data=result_to_show,data2 = recommandation_wise_result,data3 = attribute_difference_recommendation_wise_level1)

    if isinstance(old_json,dict):
        old_json = scoop_json(old_json, -1, "recommendations.results")
    else:
        old_json = scoop_json(old_json, 0, "results")

    if isinstance(new_json,dict):
        new_json = scoop_json(new_json, -1, "recommendations.results")
    else:
        new_json = scoop_json(new_json, 0, "results")

    add_data_to_result_to_show(result_to_show, 'Length of results in File 1 without filter ' + str(len(old_json)))
    add_data_to_result_to_show(result_to_show, 'Length of results in File 2 without filter ' + str(len(new_json)))

    # create dictionary and filter according to airline
    services = request.form['service']
    old_dictionary = convert_list_to_dic_and_filter(old_json, request.form['dictionary_id_1'],
                                                    "REM_AFTER_LAST_UNDERSCORE", services)
    new_dictionary = convert_list_to_dic_and_filter(new_json, request.form['dictionary_id_2'],
                                                    "REM_AFTER_LAST_UNDERSCORE", services)

    old_json = None
    new_json = None

    add_data_to_result_to_show(result_to_show, 'Length of results in File 1 after filter ' + str(len(old_dictionary)))
    add_data_to_result_to_show(result_to_show, 'Length of results in File 2 after filter ' + str(len(new_dictionary)))


    if not isinstance(old_dictionary, dict):
        add_data_to_result_to_show(result_to_show, "Unable to convert dictionary for file 1 , Internal Error")
        return render_template("singleresult.html", data=result_to_show,data2 = recommandation_wise_result,data3=attribute_difference_recommendation_wise_level1)
    if not isinstance(new_dictionary, dict):
        add_data_to_result_to_show(result_to_show, "Unable to convert dictionary for file 2 , Internal Error")
        return render_template("singleresult.html", data=result_to_show,data2 = recommandation_wise_result,data3=attribute_difference_recommendation_wise_level1)

    start_compare_recommendations_dictionary(old_dictionary, new_dictionary, result_to_show, recommandation_wise_result,attribute_difference_recommendation_wise_level1,attribute_difference_recommendation_nested)
    return render_template('singleresult.html', data=result_to_show,data2 = recommandation_wise_result,data3 = attribute_difference_recommendation_wise_level1,data4 =attribute_difference_recommendation_nested)



@app.route('/searchcomparebatchsmart',methods=['POST'])
def batch_search_comparator_lage_raho():
    data = load_file_from_upload(request.files['batch'])
    url1 = data['host1']+'/international/json/listing/'+data['lob1']
    url2 = data['host2']+'/international/json/listing/'+data['lob2']
    arrayoftriptype = ['OW','RT']

    case_wise_result_to_show = {}
    case_wise_recommandation_wise_result = {}
    case_wise_attribute_difference_recommendation_wise = {}
    attribute_difference_recommendation_nested = {}
    month_array = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP',"OCT",'NOV','DEC']
    for case in data['cases']:
        fromcity = case['from']
        tocity = case['to']
        for rtcase in arrayoftriptype:
            today = date.today()
            current_month = today.month+2
            current_year = today.year
            if current_month > 12:
                current_month = 2
                current_year = current_year + 1

            start_date = ["1"+month_array[current_month-1]+str(current_year),"2"+month_array[current_month-1]+str(current_year),
                          "3"+month_array[current_month-1]+str(current_year),"4"+month_array[current_month-1]+str(current_year),
                          "5"+month_array[current_month-1]+str(current_year),"6"+month_array[current_month-1]+str(current_year),"7"+month_array[current_month-1]+str(current_year)]
            end_date = ["11"+month_array[current_month-1]+str(current_year),"12"+month_array[current_month-1]+str(current_year),
                        "13"+month_array[current_month-1]+str(current_year),"14"+month_array[current_month-1]+str(current_year),
                        "15"+month_array[current_month-1]+str(current_year),"16"+month_array[current_month-1]+str(current_year),"17"+month_array[current_month-1]+ str(current_year)]
            datecounter = 0
            for datecase in start_date:
                paxtypearray = ['A-1','A-2','A-1-C-1','A-2-C-1','A-1-C-1-I-1','A-2-C-1-I-1','A-2-C-2-I-1']
                q1 = fromcity+"-"+tocity+"-D-"+datecase
                if(rtcase == 'RT'):
                    q1 = q1 +"_"+tocity+"-"+fromcity+"-D-"+end_date[datecounter]
                    datecounter = datecounter+1

                for paxcase in paxtypearray:
                    cabinarray = ['E','B','F','PE']
                    for cabincase in cabinarray:
                        case_of_fire = "/"+rtcase+"/"+q1+"/"+paxcase+"/"+cabincase
                        first_url_final = url1+case_of_fire
                        second_url_final = url2+case_of_fire

                        result_to_show = []
                        recommandation_wise_result = {}
                        attribute_difference_recommendation_wise = {}
                        attribute_difference_recommendation_wise_nested = {}
                        case_wise_result_to_show[case_of_fire] = result_to_show
                        case_wise_recommandation_wise_result[case_of_fire]= recommandation_wise_result
                        case_wise_attribute_difference_recommendation_wise[case_of_fire] = attribute_difference_recommendation_wise
                        attribute_difference_recommendation_nested[case_of_fire] = attribute_difference_recommendation_wise_nested

                        # load Files From Url
                        old_json = file_from_url(first_url_final)
                        new_json = file_from_url(second_url_final)
                        if old_json == "Connection Error":
                            add_data_to_result_to_show(result_to_show, "Error while uploading File 1")
                            continue
                            #return render_template('result.html', data=result_to_show,data2 = recommandation_wise_result,data3 = attribute_difference_recommendation_wise)
                        if new_json == "Connection Error":
                            add_data_to_result_to_show(result_to_show, "Error while uploading File 2")
                            continue
                            #return render_template('result.html', data=result_to_show,data2 = recommandation_wise_result,data3 = attribute_difference_recommendation_wise)

                        old_json = scoop_json(old_json, 0, "results")
                        new_json = scoop_json(new_json, 0, "results")

                        add_data_to_result_to_show(result_to_show, 'Length of results in File 1 without filter ' + str(len(old_json)))
                        add_data_to_result_to_show(result_to_show, 'Length of results in File 2 without filter ' + str(len(new_json)))

                        # create dictionary and filter according to airline
                        services = request.form['service']
                        old_dictionary = convert_list_to_dic_and_filter(old_json, request.form['dictionary_id_1'],
                                                        "REM_AFTER_LAST_UNDERSCORE", services)
                        new_dictionary = convert_list_to_dic_and_filter(new_json, request.form['dictionary_id_2'],
                                                        "REM_AFTER_LAST_UNDERSCORE", services)

                        old_json = None
                        new_json = None

                        add_data_to_result_to_show(result_to_show, 'Length of results in File 1 after filter ' + str(len(old_dictionary)))
                        add_data_to_result_to_show(result_to_show, 'Length of results in File 2 after filter ' + str(len(new_dictionary)))


                        if not isinstance(old_dictionary, dict):
                            add_data_to_result_to_show(result_to_show, "Unable to convert dictionary for file 1 , Internal Error")
                            continue
                            #return render_template("result.html", data=result_to_show,data2 = recommandation_wise_result,data3=attribute_difference_recommendation_wise)
                        if not isinstance(new_dictionary, dict):
                            add_data_to_result_to_show(result_to_show, "Unable to convert dictionary for file 2 , Internal Error")
                            continue
                            #return render_template("result.html", data=result_to_show,data2 = recommandation_wise_result,data3=attribute_difference_recommendation_wise)

                        start_compare_recommendations_dictionary(old_dictionary, new_dictionary, result_to_show, recommandation_wise_result,attribute_difference_recommendation_wise,attribute_difference_recommendation_wise_nested)


    return render_template('result.html', data=case_wise_result_to_show,data2 = case_wise_recommandation_wise_result,
                           data3 = case_wise_attribute_difference_recommendation_wise,data4 = attribute_difference_recommendation_nested)









if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
