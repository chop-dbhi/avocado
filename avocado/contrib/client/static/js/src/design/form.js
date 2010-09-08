require.def('design/form', ['lib/jquery.jqote2'], {
    
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
                                            '<input id="<%=this.field_id%>_input0" type="text" name="<%=this.field_id%>_input0" size="5">',
                                            '<label for="<%=this.field_id%>_input1">and</label>',
                                            '<input id="<%=this.field_id%>_input1" type="text" name="<%=this.field_id%>_input1" size="5">'];
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
               
               $form.append($.jqote(input.join(""), {"choices":element.choices,"field_id":concept_pk+"_"+element.pk, "label":element.label}));
         });
         
         // Trigger an event when anything changes
         $("input,select",$form).change(function(evt){
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
                                                     if (opt.value.search("range") === -1){
                                                         $("input[name="+opt.id+"_input1],",$form).hide().change();
                                                         $("label[for="+opt.id+"_input1]",$form).hide();
                                                     }else{
                                                         $("input[name="+opt.id+"_input1]",$form).show().change();
                                                         $("label[for="+opt.id+"_input1]",$form).show();
                                                     }
                                                 }
                                             });
                                             // Since this code executes for select choices boxes as well as operators (which should
                                             // never be plural), we make sure to send the correct type array, or single item
                                             var sendValue = evt.target.type === "select-multiple" ? selected : selected[0]; // JMM I am concerned selcted[0] could sometimes be undefined?
                                             //var sendValue = selected;
                                             $form.trigger("ElementChangedEvent", [{name:evt.target.name, value:sendValue}]);
                                             break;
                    default   : // This catches input boxes, if input boxes are not currently visible, send null for them
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
                 if ($element.length == 0) return;
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
                     default   :    //inputs and singular selects 
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