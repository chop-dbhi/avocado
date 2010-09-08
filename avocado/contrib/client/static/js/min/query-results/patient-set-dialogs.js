var $saveDialog,
    $deleteDialog;

$(document).ready(function() {
    var $saveForm = $('#save-form').submit(function(evt) {
		evt.preventDefault();
	});
    
    $saveDialog = $('#save-dialog').dialog({
        autoOpen: false,
        modal: true,
        draggable: true,
        resizable: false,
        title: 'Edit Patient Set Details',
        width: 400,
        buttons: {
            Cancel: function() {
                $saveDialog.dialog('close');
            },
            Save: function() {
                var url = $saveForm.attr('action'),
                    data = $saveForm.serialize();
                
                if (/name=\+*&/.test(data)) {
                    $saveForm.siblings('#errors').show();
                    return;
                }
                
                $.post(url, data, function(json) {
                    ajaxSuccess(json);

                    if (json.success) {
                        if (json.url) {
                            window.location = json.url;
                        } else {
                            $saveForm.siblings('#errors').hide();
                            $unsavedSetMsg.hide();
                            $objSetInfo.html(json.setinfo).show();
                            $saveDialog.dialog('close');
                        }
                    }
                });
            }
        }
    });   

    $deleteDialog = $('#delete-dialog').dialog({
        autoOpen: false,
        modal: true,
        draggable: false,
        resizable: false,
        title: 'Delete this Patient Set?',
        width: 300,
        buttons: {
            No: function() {
                $deleteDialog.dialog('close');
            },
            Yes: function() {
                var url = $('.delete-patient-set').attr('href');
                $.post(url, {}, function(json) {
                    ajaxSuccess(json);
                    if (json.success) {
                        if (json.url)
                            window.location = json.url;
                    }
                });
            }
        }
    }); 

});