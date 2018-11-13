'use strict';

function show_element(id, type='block') {
	show(document.getElementById(id), type);
}

function hide_element(id) {
	hide(document.getElementById(id));
}

function show_button(id) {
	elem=document.getElementById(id).parentElement;
	show(elem, 'block');
}

function hide_button(id) {
	elem=document.getElementById(id).parentElement;
	hide(elem);
}

function show(element, type) {
	element.classList.remove("d-none");

	element.classList.add('d-'+type);
}

function hide(element) {
	element.classList.remove('d-block', 'd-inline');

	element.classList.add('d-none');
}

function hide_message() {
	hide_element('alert_messages');
}

function show_message(message, type='success') {
	elem=document.getElementById('alert_message');

	elem.classList.remove('alert-success', 'alert-info', 'alert-warning', 'alert-danger');
	elem.classList.add('alert-'+type);

	elem.innerHTML=message;

	show_element('alert_messages')
}