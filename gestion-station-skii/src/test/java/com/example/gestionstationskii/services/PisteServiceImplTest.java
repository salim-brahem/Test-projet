package com.example.gestionstationskii.services;

import com.example.gestionstationskii.entities.Color;
import com.example.gestionstationskii.entities.Piste;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Slf4j
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@DisplayName("Tests d'intégration Piste Service")
class PisteServiceImplTest {

    @Autowired
    private IPisteServices pisteServices;

    private static Long savedPisteId;

    @Test
    @Order(1)
    @DisplayName("Test d'ajout d'une piste")
    void testAddPiste() {
        log.info("🚀 Début du test testAddPiste");
        
        Piste p = new Piste();
        p.setNamePiste("TestPiste");
        p.setColor(Color.BLUE);
        p.setLength(1500);
        p.setSlope(25);

        Piste savedPiste = pisteServices.addPiste(p);
        savedPisteId = savedPiste.getNumPiste();
        
        log.info("✅ Piste ajoutée avec ID : {}", savedPisteId);

        assertNotNull(savedPisteId, "L'ID de la piste ne doit pas être null");
        assertEquals("TestPiste", savedPiste.getNamePiste());
        assertEquals(Color.BLUE, savedPiste.getColor());
        assertEquals(1500, savedPiste.getLength());
        assertEquals(25, savedPiste.getSlope());
        
        log.info("✅ Test testAddPiste terminé avec succès");
    }

    @Test
    @Order(2)
    @DisplayName("Test de récupération de toutes les pistes")
    void testRetrieveAllPistes() {
        log.info("🚀 Début du test testRetrieveAllPistes");
        
        List<Piste> pistes = pisteServices.retrieveAllPistes();
        log.info("📋 Nombre total de pistes : {}", pistes.size());
        
        assertNotNull(pistes, "La liste des pistes ne doit pas être null");
        assertFalse(pistes.isEmpty(), "La liste des pistes ne doit pas être vide");
        assertTrue(pistes.size() >= 1, "Doit contenir au moins la piste créée");
        
        log.info("✅ Test testRetrieveAllPistes terminé avec succès");
    }

    @Test
    @Order(3)
    @DisplayName("Test de récupération d'une piste par ID")
    void testRetrievePiste() {
        log.info("🚀 Début du test testRetrievePiste");
        
        assertNotNull(savedPisteId, "L'ID de la piste sauvegardée ne doit pas être null");
        
        Piste retrieved = pisteServices.retrievePiste(savedPisteId);
        log.info("🔍 Piste récupérée : {}", retrieved);
        
        assertNotNull(retrieved, "La piste récupérée ne doit pas être null");
        assertEquals(savedPisteId, retrieved.getNumPiste());
        assertEquals("TestPiste", retrieved.getNamePiste());
        assertEquals(Color.BLUE, retrieved.getColor());
        
        log.info("✅ Test testRetrievePiste terminé avec succès");
    }

    @Test
    @Order(4)
    @DisplayName("Test de mise à jour d'une piste")
    void testUpdatePiste() {
        log.info("🚀 Début du test testUpdatePiste");
        
        assertNotNull(savedPisteId, "L'ID de la piste sauvegardée ne doit pas être null");
        
        Piste existingPiste = pisteServices.retrievePiste(savedPisteId);
        assertNotNull(existingPiste, "La piste existante doit être récupérée");
        
        existingPiste.setNamePiste("TestPisteModifiée");
        existingPiste.setColor(Color.RED);
        existingPiste.setLength(1600);
        existingPiste.setSlope(30);

        Piste updatedPiste = pisteServices.updatePiste(existingPiste);
        
        log.info("✏️ Piste modifiée : {}", updatedPiste);

        assertNotNull(updatedPiste, "La piste mise à jour ne doit pas être null");
        assertEquals("TestPisteModifiée", updatedPiste.getNamePiste());
        assertEquals(Color.RED, updatedPiste.getColor());
        assertEquals(1600, updatedPiste.getLength());
        assertEquals(30, updatedPiste.getSlope());
        
        log.info("✅ Test testUpdatePiste terminé avec succès");
    }

    @Test
    @Order(5)
    @DisplayName("Test de suppression d'une piste")
    void testRemovePiste() {
        log.info("🚀 Début du test testRemovePiste");
        
        assertNotNull(savedPisteId, "L'ID de la piste sauvegardée ne doit pas être null");
        
        // Vérifier que la piste existe avant suppression
        Piste existingPiste = pisteServices.retrievePiste(savedPisteId);
        assertNotNull(existingPiste, "La piste doit exister avant la suppression");

        // Supprimer la piste
        pisteServices.removePiste(savedPisteId);
        
        log.info("🗑️ Piste avec ID {} supprimée", savedPisteId);

        // Vérifier que la piste n'existe plus
        Piste deletedPiste = pisteServices.retrievePiste(savedPisteId);
        log.info("❌ Piste après suppression : {}", deletedPiste);
        
        assertNull(deletedPiste, "La piste devrait être null après suppression");
        
        log.info("✅ Test testRemovePiste terminé avec succès");
    }

    @BeforeEach
    void setUp() {
        log.info("🔧 Configuration du test");
    }

    @AfterEach
    void tearDown() {
        log.info("🧹 Nettoyage après test");
    }
}