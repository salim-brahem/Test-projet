package com.example.gestionstationskii.services;

import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import com.example.gestionstationskii.entities.Piste;
import com.example.gestionstationskii.repositories.IPisteRepository;

import java.util.List;

@AllArgsConstructor
@Service
public class PisteServicesImpl implements IPisteServices {

    private IPisteRepository pisteRepository;

    @Override
    public List<Piste> retrieveAllPistes() {
        System.out.println("[PisteServices] → Récupération de toutes les pistes");
        List<Piste> pistes = pisteRepository.findAll();
        System.out.println("[PisteServices] → Nombre de pistes trouvées : " + pistes.size());
        return pistes;
    }

    @Override
    public Piste addPiste(Piste piste) {
        System.out.println("[PisteServices] → Ajout d'une nouvelle piste : " + piste);
        Piste savedPiste = pisteRepository.save(piste);
        System.out.println("[PisteServices] → Piste ajoutée avec succès : " + savedPiste);
        return savedPiste;
    }

    @Override
    public void removePiste(Long numPiste) {
        System.out.println("[PisteServices] → Suppression de la piste avec ID : " + numPiste);
        pisteRepository.deleteById(numPiste);
        System.out.println("[PisteServices] → Suppression terminée");
    }

    @Override
    public Piste retrievePiste(Long numPiste) {
        System.out.println("[PisteServices] → Récupération de la piste avec ID : " + numPiste);
        Piste piste = pisteRepository.findById(numPiste).orElse(null);
        if (piste != null) {
            System.out.println("[PisteServices] → Piste trouvée : " + piste);
        } else {
            System.out.println("[PisteServices] → Aucune piste trouvée avec cet ID");
        }
        return piste;
    }

    @Override
    public Piste updatePiste(Piste piste) {
        return pisteRepository.save(piste); // JPA gère automatiquement l'update si l'ID existe
    }
}
