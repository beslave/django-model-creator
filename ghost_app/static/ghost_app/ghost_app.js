(function ($){
    $(document).ready(function(){
        prepareInput($('.js-input'));
        $('.js-object-field').click(createInput);
    });

    function prepareInput(elements){
        $.each(elements, function(i, element){
            var element = $(element);
            switch(element.data('type')){
                case 'int':
                    element.keyup(function(e){
                        this.value = this.value.replace(/[^0-9]/g, '');
                    });
                    break
                case 'char':
                    break
                case 'date':
                case 'datetime':
                    element.datepicker({dateFormat: 'yy-mm-dd'});
                    break
            };
        });
    }

    function createInput(e){
        clearAllInputs();
        var input = $('<input class="js-object-field-input b-object-field-input" type="text" value="' + $(this).text().trim() + '" />');
        $(this).append(input);
    };

    function clearAllInputs(){
        $('.js-object-field-input').remove();
    };
})(jQuery);