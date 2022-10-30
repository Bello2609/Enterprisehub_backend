function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function addForm(btn, prefix) {
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());

    var row = $('.dynamic-form:first').clone(true).get(0);
    $(row).removeAttr('id').insertAfter($('.dynamic-form:last')).find('.hidden').removeClass('hidden');
    $(row).find("ul.errorlist").remove();
    $(row).children().not(':last').children().each(function () {
        updateElementIndex(this, prefix, formCount);
        // This is the ONLY custom part and can be subtituded with the more generic  $(this).val('');
        if($(this).prop("id").indexOf("discount") === -1){
            $(this).val('');
        }else {
            $(this).val(0);
        }

    });
    $(row).find('.delete-row').click(function () {
        deleteForm(this, prefix);
    });
    $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
    return false;
}

function deleteForm(btn, prefix) {
    $(btn).parents('.dynamic-form').remove();
    var forms = $('.dynamic-form');
    $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
    for (var i = 0, formCount = forms.length; i < formCount; i++) {
        $(forms.get(i)).children().not(':last').children().each(function () {
            updateElementIndex(this, prefix, i);
        });
    }
    return false;
}

$(function () {
    $('.add-row').click(function() {
        return addForm(this, 'purchase');
    });
    $('.delete-row').click(function() {
        return deleteForm(this, 'purchase');
    })
});



//******************************** :New Start: *********************************//
$('#add_more').click(function() {
    cloneMore('div.table:last', 'service');
});

function cloneMore(selector, type) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}