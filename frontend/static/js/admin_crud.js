document.addEventListener("DOMContentLoaded", function() {
    const tableBody = document.getElementById("pokemon-table-body");
    const form = document.getElementById("pokemon-form");
    const formTitle = document.getElementById("form-title");
    const btnSubmit = document.getElementById("btn-submit");
    const btnCancel = document.getElementById("btn-cancel");

    const pokemonIdInput = document.getElementById("pokemon-id");
    const pokedexNumberInput = document.getElementById("pokedex_number");
    const nameInput = document.getElementById("name");
    const type1Select = document.getElementById("type1");
    const type2Select = document.getElementById("type2");
    const hpInput = document.getElementById("hp");
    const attackInput = document.getElementById("attack");
    const defenseInput = document.getElementById("defense");
    const imageUrlInput = document.getElementById("image_url");

    //Elementos de búsqueda y filtrado
    const searchNameInput = document.getElementById("search-name");
    const filterTypeSelect = document.getElementById("filter-type");

    let pokemonList = [];

    // 1. CARGAR LOS TIPOS OFICIALES EN LOS DESPLEGABLES
    function loadTypes() {
        return fetch("/api/types")
            .then(res => res.json())
            .then(types => {
                type1Select.innerHTML = "";
                type2Select.innerHTML = '<option value="">Ninguno</option>';
                //Resetear también el select del filtro superior
                filterTypeSelect.innerHTML = '<option value="">All Types (Todos)</option>';
                
                types.forEach(t => {
                    const opt1 = `<option value="${t.id}">${t.name}</option>`;
                    const opt2 = `<option value="${t.id}">${t.name}</option>`;
                    const optFilter = `<option value="${t.name}">${t.name}</option>`; // 🔄 NUEVO: Filtramos por el nombre del tipo
                    
                    type1Select.innerHTML += opt1;
                    type2Select.innerHTML += opt2;
                    filterTypeSelect.innerHTML += optFilter; // 🔄 NUEVO
                });
            });
    }

    // 2. CARGAR Y LISTAR POKÉMONS
    function loadPokemons() {
        fetch("/api/pokemons")
            .then(res => res.json())
            .then(data => {
                pokemonList = data;
                renderPokemonTable(pokemonList); // Modularizado en una función aparte
            });
    }

    //FUNCIÓN EXCLUSIVA PARA PINTAR LA TABLA (Permite pasarle listas filtradas)
    function renderPokemonTable(listToRender) {
        tableBody.innerHTML = "";
        
        if (listToRender.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="6" style="padding:15px; text-align:center; color: #888;">No se encontraron Pokémon con esos criterios.</td></tr>`;
            return;
        }

        listToRender.forEach(p => {
            const types = p.type2_name ? `${p.type1_name} / ${p.type2_name}` : p.type1_name;
            const img = p.image_url ? `<img src="${p.image_url}" width="50" height="50" style="object-fit:contain;">` : '❌';
            
            const row = document.createElement("tr");
            row.style.borderBottom = "1px solid #ddd";
            row.innerHTML = `
                <td style="padding:10px;">#${p.pokedex_number}</td>
                <td style="padding:10px; text-align:center;">${img}</td>
                <td style="padding:10px;"><strong>${p.name}</strong></td>
                <td style="padding:10px;"><span style="background:#ddd; padding:3px 8px; border-radius:10px; font-size:12px;">${types}</span></td>
                <td style="padding:10px; font-size: 13px;">HP:${p.hp} | A:${p.attack} | D:${p.defense}</td>
                <td style="padding:10px; text-align:center;">
                    <button class="btn-edit" data-id="${p.id}" style="background:#ffc107; border:none; padding:5px 8px; border-radius:3px; cursor:pointer; margin-right:5px;">✏️</button>
                    <button class="btn-delete" data-id="${p.id}" style="background:#dc3545; color:white; border:none; padding:5px 8px; border-radius:3px; cursor:pointer;">🗑️</button>
                </td>
            `;
            tableBody.appendChild(row);
        });

        document.querySelectorAll(".btn-edit").forEach(btn => btn.addEventListener("click", handleEdit));
        document.querySelectorAll(".btn-delete").forEach(btn => btn.addEventListener("click", handleDelete));
    }

    // LÓGICA DE FILTRADO COMBINADO (Nombre + Tipo)
    function filterPokemons() {
        const searchTerm = searchNameInput.value.toLowerCase().trim();
        const selectedType = filterTypeSelect.value;

        const filtered = pokemonList.filter(p => {
            // Validar coincidencia por Nombre o Número de Pokédex
            const matchesNameOrNum = p.name.toLowerCase().includes(searchTerm) || 
                                     p.pokedex_number.toString().includes(searchTerm);
            
            // Validar coincidencia por Tipo (en tipo 1 o tipo 2)
            const matchesType = selectedType === "" || 
                                p.type1_name === selectedType || 
                                p.type2_name === selectedType;

            return matchesNameOrNum && matchesType;
        });

        renderPokemonTable(filtered);
    }

    // Escuchadores de eventos para los filtros (se activa al escribir o cambiar select)
    searchNameInput.addEventListener("input", filterPokemons);
    filterTypeSelect.addEventListener("change", filterPokemons);


    // 3. ENVIAR FORMULARIO (CREAR O EDITAR)
    form.addEventListener("submit", function(e) {
        e.preventDefault();

        const id = pokemonIdInput.value;
        const payload = {
            pokedex_number: pokedexNumberInput.value,
            name: nameInput.value,
            type1_id: type1Select.value,
            type2_id: type2Select.value || null,
            hp: hpInput.value,
            attack: attackInput.value,
            defense: defenseInput.value,
            image_url: imageUrlInput.value || ""
        };

        const isEditing = id !== "";
        const url = isEditing ? `/api/pokemons/${id}` : "/api/pokemons";
        const method = isEditing ? "PUT" : "POST";

        fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(resData => {
            if (resData.success) {
                alert(resData.message);
                resetForm();
                loadPokemons();
            } else {
                alert("Error: " + resData.error);
            }
        });
    });

    // 4. PASAR A MODO EDICIÓN
    function handleEdit(e) {
        const id = e.currentTarget.getAttribute("data-id");
        const p = pokemonList.find(item => item.id == id);

        if (p) {
            formTitle.innerText = `✏️ Editando a ${p.name}`;
            btnSubmit.innerText = "Actualizar Cambios";
            btnSubmit.style.background = "#007bff";
            btnCancel.style.display = "block";

            pokemonIdInput.value = p.id;
            pokedexNumberInput.value = p.pokedex_number;
            nameInput.value = p.name;
            type1Select.value = p.type1_id;
            type2Select.value = p.type2_id || "";
            hpInput.value = p.hp;
            attackInput.value = p.attack;
            defenseInput.value = p.defense;
            imageUrlInput.value = p.image_url || "";
        }
    }

    // 5. BORRAR POKÉMON
    function handleDelete(e) {
        const id = e.currentTarget.getAttribute("data-id");
        if (confirm("¿Seguro que quieres eliminar este Pokémon?")) {
            fetch(`/api/pokemons/${id}`, { method: "DELETE" })
                .then(res => res.json())
                .then(resData => {
                    if (resData.success) {
                        alert(resData.message);
                        loadPokemons();
                    }
                });
        }
    }

    function resetForm() {
        formTitle.innerText = "➕ Añadir Nuevo Pokémon";
        btnSubmit.innerText = "Guardar Pokémon";
        btnSubmit.style.background = "#28a745";
        btnCancel.style.display = "none";
        pokemonIdInput.value = "";
        form.reset();
        
        // Limpiar filtros al guardar/editar para ver los resultados limpios
        searchNameInput.value = "";
        filterTypeSelect.value = "";
    }

    btnCancel.addEventListener("click", resetForm);

    // Flujo inicial: Primero cargar los tipos desplegables, luego pintar los pokémon
    loadTypes().then(loadPokemons);
});