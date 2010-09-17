require.def('design/form', [], {
    
    Form : function(view, concept_pk){
          var $form = $('<form method="get" action=""></form>');
          var decOperatorsTmpl =  ['<option id="<%=this.field_id%>" value="range">is between</option>',
                                   '<option id="<%=this.field_id%>" value="exclude:range">is not between</option>',
                                   '<option id="<%=this.field_id%>" value="lt">is less than</option>',
                                   '<option id="<%=this.field_id%>" value="gt">is greater than</option>',
                                   '<option id="<%=this.field_id%>" value="lte">is less than or equal to</option>',
                                   '<option id="<%=this.field_id%>" value="gte">is greater than or equal to</option>',
                                   '<option id="<%=this.field_id%>" value="exact">is equal to</option>',
                                   '<option id="<%=this.field_id%>" value="exclude:exact">is not equal to</option>'].join('');
          var choiceOperatorsTmpl = ['<option value="in">is equal to</option>',
                                     '<option value="exclude:in">is not equal to</option>'].join('');

          $.each(view.fields, function(index,element){
              var input;
              switch (element.datatype) {
                  case 'boolean':  input = ['<label for="<%=this.field_id%>"><%=this.label%></label>',
                                            '<select id ="<%=this.field_id%>" name="<%=this.field_id%>">',
                                                '<option value="Yes">Yes</option>',
                                                '<option value="No">No</option>',
                                            '</select>'];
                                   break;
                  case 'assertion':input = ['<input type="checkbox" name="<%=this.field_id%>" value="<%=this.field_id%>"/><%=this.label%>',
                                            '</select>'];
                                   break;
                  case 'decimal'  :input = ['<label for="<%=this.field_id%>"><%=this.label%></label>',
                                            '<select id="<%=this.field_id%>_operator" name="<%=this.field_id%>_operator">',
                                               decOperatorsTmpl,
                                            '</select>',
                                            '<span class="input_association" name="<%=this.field_id%>_input_assoc">',
                                            '<input data-validate="decimal" id="<%=this.field_id%>_input0" type="text" name="<%=this.field_id%>_input0" size="5">',
                                            '<label for="<%=this.field_id%>_input1">and</label>',
                                            '<input data-validate="decimal" id="<%=this.field_id%>_input1" type="text" name="<%=this.field_id%>_input1" size="5">',
                                            '</span>'];
                                   break;
                 case 'choice'    : input = [ '<label for="<%=this.field_id%>"><%=this.label%></label>',
                                              '<select id="<%=this.field_id%>-operator" name="<%=this.field_id%>_operator">',
                                                 choiceOperatorsTmpl,
                                              '</select>',
                                              '<select multiple="multiple" id="<%=this.field_id%>-value" name="<%=this.field_id%>" size="7">',
                                              '<% for (index in this.choices) { %>',
                                                    '<option value="<%=this.choices[index][0]%>"><%=this.choices[index][1]%></option>',
                                               '<%}%>',
                                              '</select>'
                                            ];
               }
               // Wrap each discrete element in <p>
               input.unshift("<p>");
               input.push("</p>");
               
               
               // This should come out, the server should send us No Data instead of null
               element.choices && $.each(element.choices, function(index, choice){
                      // null needs to be "No Data"
                      if (element.choices[index][0] === null){
                          element.choices[index][0] = "No Data";
                      }
                      if (element.choices[index][1] === "None"){
                           element.choices[index][1] = "No Data";
                      }
                });
               
               $form.append($.jqote(input.join(""), {"choices":element.choices,"field_id":concept_pk+"_"+element.pk, "label":element.name}));
         });
         // Trigger an event when anything changes
         $("input,select",$form).bind('change keyup', function(evt){
            switch (evt.target.type){
                    case "checkbox": $form.trigger("ElementChangedEvent", [{name:evt.target.name,value:evt.target.checked}]);
                                     break;
                    case "select-one"      :
                    case "select-multiple" : 
                    case "select"          : var selected = []; 
                                              $("option", $(evt.target)).each(function(index,opt){
                                                 if  (opt.selected){
                                                     selected.push(opt.value);
                                                     // Do we need to show two inputs?
                                                     
                                                     if (opt.value.search(/range/) === -1){
                                                         $("input[name="+opt.id+"_input1],",$form).hide().change();
                                                         $("label[for="+opt.id+"_input1]",$form).hide();
                                                         // Trigger change on associated inputs because they need to work with a range operator now
                                                         $("input[name="+opt.id+"_input0]",$form).change();
                                                     }else{
                                                         $("input[name="+opt.id+"_input1]",$form).show().change();
                                                         $("label[for="+opt.id+"_input1]",$form).show();
                                                         // Trigger change on associated inputs because they need to work with a range operator now
                                                         $("input[name="+opt.id+"_input0]",$form).change();
                                                     }
                                                 }
                                             });
                                             // Since this code executes for select choices boxes as well as operators (which should
                                             // never be plural), we make sure to send the correct type array, or single item
                                             var sendValue = evt.target.type === "select-multiple" ? selected : selected[0]; // JMM I am concerned selected[0] could sometimes be undefined?
                                             $form.trigger("ElementChangedEvent", [{name:evt.target.name, value:sendValue}]);
                                             break;
                    default   : // This catches input boxes, if input boxes are not currently visible, send null for them
                                // Input boxes require an extra validation step because of the free form input
                                
                                var associated_operator = $(evt.target).parent().parent().find('select').val();
                                var name_prefix = evt.target.name.substr(0,evt.target.name.length-1);
                                var $input1 = $("input[name="+name_prefix+"0]",$form);
                                var $input2 = $("input[name="+name_prefix+"1]",$form);
                                var value1 = parseFloat($input1.val());
                                var value2 = parseFloat($input2.val());
                                var $target = $(evt.target);
                                // This one is a little tricky because it matters not just that the fields map to valid numbers
                                // but that in the case of a range style operator, the two numbers are sequential, and finally
                                // if fields have become hidden due to a change in operator, we no longer want to list that something
                                // is wrong with the field even if there is (because it doesn't matter)
                                switch ($(evt.target).attr('data-validate')){
                                    case "decimal": if (($target.css("display") !== "none") && isNaN(Number(evt.target.value))) {
                                                        // Field contains a non-number and is visible
                                                        var input_evt = $.Event("InvalidInputEvent");
                                                        $(evt.target).trigger(input_evt);
                                                    }else if ($(evt.target).hasClass('invalid')){ //TODO Don't rely on this
                                                        // Field either contains a number or is not visible
                                                        // Either way it was previously invalid
                                                        input_evt = $.Event("InputCorrectedEvent");
                                                        $(evt.target).trigger(input_evt);
                                                    } else if ((associated_operator.search(/range/) >= 0) && (value1 > value2) && ($input2.css("display") != "none")) {
                                                        // A range operator is in use, both fields are visible, and their values are not sequential
                                                        input_evt = $.Event("InvalidInputEvent");
                                                        input_evt.reason = "badrange";
                                                        input_evt.message = "First input must be less than second input.";
                                                        $(evt.target).parent().trigger(input_evt);
                                                    } else if ($(evt.target).parent().hasClass('invalid_badrange') && (($input2.css("display") === "none")||(value1 < value2))){ //TODO Don't really on this
                                                        // A range operator is or was in use, and either a range operator is no longer in use, so we don't care, or 
                                                        // its in use but the values are now sequential.
                                                        input_evt = $.Event("InputCorrectedEvent");
                                                        input_evt.reason = "badrange";
                                                        $(evt.target).parent().trigger(input_evt);
                                                    }   
                                                    break;
                                    default: break;
                                }
                                var value = $(evt.target).css("display") !== "none" ? evt.target.value : null;
                                $form.trigger("ElementChangedEvent", [{name:evt.target.name,value:value}]);
                                break;
             }
             evt.stopPropagation();
         });
         
         
         var updateElement = function(evt, element) {
                 var $element = $("[name="+element.name+"]", $form);
                 // Note: Just because we are here doesn't mean we contain the element
                 // to be updated
                 if ($element.length === 0) return;
                 var type = $element.attr("type");
                 switch (type){
                     case "checkbox": $element.attr("checked",element.value);
                                      break;
                     case "select-multiple" : $("option", $element).each(function(index,opt){
                                                  if ($.inArray(opt.value,element.value)!=-1){
                                                      opt.selected = true;
                                                  }else{
                                                      opt.selected = false;
                                                  }
                                              });
                                              break; 
                     default:   // inputs and singular selects 
                                $element.attr("value",element.value); 
                                break;
                 }
                 
         };
         
         $form.bind("UpdateElementEvent", updateElement);
         
         $form.bind("UpdateDSEvent", function(evt, ds){
             for (var key in ds){
                 updateElement(null, {name:key, value:ds[key]});
             }
         });
         
         $form.bind("GainedFocusEvent", function(evt) {
             $("input,select", $form).change(); 
         });
         
         return $form;
    }
});