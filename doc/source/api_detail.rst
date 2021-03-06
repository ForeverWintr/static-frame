.. _api-detail:

API Detail
===============================

For each container, the complete public API is presented below. Note that interface endpoints are expanded to show all interface sub components.

This is the full API documentation; for an overview, see :ref:`api-overview`.


.. jinja:: ctx

    {% for name, cls, frame in interface %}

    {{ name }}
    -------------------------------------------------

    .. autoclass:: static_frame.{{cls.__name__}}

    {% for group, frame_sub in frame.iter_group_items('group', axis=0) %}

    .. _api-detail-{{ name }}-{{ group }}:

    {{ name }}: {{ group }}
    ..........................................................

    Overview: :ref:`api-overview-{{ name }}-{{ group }}`

    {% for signature, row in frame_sub.iter_tuple_items(axis=1) -%}



    {% if row.use_signature and signature.startswith('[') %}

    .. py:method:: {{ name }}{{ signature }}  {# NOTE: no dot! #}

    {% elif row.use_signature and signature.startswith('interface') %}

    .. py:attribute:: {{ name }}.{{ signature }}

        {{ row.doc }}

    {% elif row.use_signature and not row.is_attr %}

    .. py:method:: {{ name }}.{{ signature }}

    {% elif row.use_signature and row.is_attr %}

    .. py:attribute:: {{ name }}.{{ signature }}

    {% elif group == 'Attribute' or signature == 'values' or row.is_attr %}

    .. autoattribute:: static_frame.{{ row.reference }}

    {% else %}

    .. automethod:: static_frame.{{ row.reference }}

    {% endif %}



    {# if a signature has been used, then we need to augment with doc with reference #}
    {% if row.use_signature %}

        {% if row.reference and row.is_attr %}

        .. autoattribute:: static_frame.{{ row.reference }}

        {% elif row.reference %}

        .. automethod:: static_frame.{{ row.reference }}

        {% endif %}

    {% endif %}



    {# if delegate_reference is defined, always include it #}
    {% if row.delegate_reference %}

        {% if row.delegate_is_attr %}

        .. autoattribute:: static_frame.{{ row.delegate_reference }}

        {% else %}

        .. automethod:: static_frame.{{ row.delegate_reference }}

        {% endif %}

    {% endif %}


    {# ---------------------------------------------------------------------- #}
    {# ``start_{{ name }}-{{ row.signature_no_args }}`` #}

    .. literalinclude:: ../../static_frame/test/unit/test_doc.py
       :language: python
       :start-after: start_{{ name }}-{{ row.signature_no_args }}
       :end-before: end_{{ name }}-{{ row.signature_no_args }}


    {% endfor %}
    {% endfor %}
    {% endfor %}


