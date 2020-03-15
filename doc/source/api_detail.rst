
API Detail
===============================



For each container, the complete public API is presented below.


.. jinja:: ctx

    {% for name, cls, frame in interface %}

    {{ name }}
    -------------------------------------------------

    .. autoclass:: static_frame.{{cls.__name__}}


    {% for group, frame_sub in frame.iter_group_items('group', axis=0) %}

    .. _api-detail-{{ name }}-{{ group }}:

    {{ name }}: {{ group }}
    ..........................................................

    API Overview: :ref:`api-overview-{{ name }}-{{ group }}`


    {% for signature, row in frame_sub.iter_tuple_items(axis=1) -%}

    {# for debuggin, write-out full row { row } #}

    {% if row.use_signature and signature.startswith('[') %}

    .. py:method:: {{ name }}{{ signature }}

    {% elif row.use_signature and signature.startswith('interface') %}

    .. py:attribute:: {{ name }}.{{ signature }}

        {{ row.doc }}

    {% elif row.use_signature %}

    .. py:method:: {{ name }}.{{ signature }}

    {% elif group == 'Attribute' or signature in ('interface', 'values') or row.reference_is_attr %}

    .. autoattribute:: static_frame.{{ row.reference }}

    {% else %}

    .. automethod:: static_frame.{{ row.reference }}

    {% endif %}


    {# if a signature has been used, then we need to augment with doc with reference #}
    {% if row.use_signature %}

        {% if row.reference and row.reference_is_attr %}

        .. autoattribute:: static_frame.{{ row.reference }}

        {% elif row.reference %}

        .. automethod:: static_frame.{{ row.reference }}

        {% endif %}

    {% endif %}


    {# if reference_end_point is defined, always include it #}
    {% if row.reference_end_point %}

        {% if row.reference_end_point_is_attr %}

        .. autoattribute:: static_frame.{{ row.reference_end_point }}

        {% else %}

        .. automethod:: static_frame.{{ row.reference_end_point }}

        {% endif %}

    {% endif %}



    {% endfor %}
    {% endfor %}
    {% endfor %}

