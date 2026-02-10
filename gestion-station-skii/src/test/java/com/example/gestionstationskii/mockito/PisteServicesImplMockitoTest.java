package com.example.gestionstationskii.mockito;

import com.example.gestionstationskii.entities.Color;
import com.example.gestionstationskii.entities.Piste;
import com.example.gestionstationskii.repositories.IPisteRepository;
import com.example.gestionstationskii.services.PisteServicesImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("Tests unitaires Piste Service avec Mockito")
class PisteServicesImplMockitoTest {

    @Mock
    private IPisteRepository pisteRepository;

    @InjectMocks
    private PisteServicesImpl pisteServices;

    private Piste testPiste;
    private Piste testPiste2;

    @BeforeEach
    void setUp() {
        // Configuration de la première piste de test
        testPiste = new Piste();
        testPiste.setNumPiste(1L);
        testPiste.setNamePiste("Piste Test 1");
        testPiste.setColor(Color.BLUE);
        testPiste.setLength(1500);
        testPiste.setSlope(25);

        // Configuration de la deuxième piste de test
        testPiste2 = new Piste();
        testPiste2.setNumPiste(2L);
        testPiste2.setNamePiste("Piste Test 2");
        testPiste2.setColor(Color.RED);
        testPiste2.setLength(2000);
        testPiste2.setSlope(30);
    }

    @Test
    @DisplayName("Récupérer toutes les pistes - Succès")
    void testRetrieveAllPistes_Success() {
        // Arrange
        List<Piste> expectedPistes = Arrays.asList(testPiste, testPiste2);
        when(pisteRepository.findAll()).thenReturn(expectedPistes);

        // Act
        List<Piste> actualPistes = pisteServices.retrieveAllPistes();

        // Assert
        assertNotNull(actualPistes);
        assertEquals(2, actualPistes.size());
        assertEquals(expectedPistes, actualPistes);
        
        // Verify
        verify(pisteRepository, times(1)).findAll();
        verifyNoMoreInteractions(pisteRepository);
    }

    @Test
    @DisplayName("Récupérer toutes les pistes - Liste vide")
    void testRetrieveAllPistes_EmptyList() {
        // Arrange
        when(pisteRepository.findAll()).thenReturn(Arrays.asList());

        // Act
        List<Piste> actualPistes = pisteServices.retrieveAllPistes();

        // Assert
        assertNotNull(actualPistes);
        assertTrue(actualPistes.isEmpty());
        
        // Verify
        verify(pisteRepository, times(1)).findAll();
        verifyNoMoreInteractions(pisteRepository);
    }

    @Test
    @DisplayName("Ajouter une piste - Succès")
    void testAddPiste_Success() {
        // Arrange
        when(pisteRepository.save(any(Piste.class))).thenReturn(testPiste);

        // Act
        Piste savedPiste = pisteServices.addPiste(testPiste);

        // Assert
        assertNotNull(savedPiste);
        assertEquals(1L, savedPiste.getNumPiste());
        assertEquals("Piste Test 1", savedPiste.getNamePiste());
        assertEquals(Color.BLUE, savedPiste.getColor());
        assertEquals(1500, savedPiste.getLength());
        assertEquals(25, savedPiste.getSlope());
        
        // Verify
        verify(pisteRepository, times(1)).save(testPiste);
        verifyNoMoreInteractions(pisteRepository);
    }

    @Test
    @DisplayName("Mettre à jour une piste - Succès")
    void testUpdatePiste_Success() {
        // Arrange
        Piste updatedPiste = new Piste();
        updatedPiste.setNumPiste(1L);
        updatedPiste.setNamePiste("Piste Modifiée");
        updatedPiste.setColor(Color.RED);
        updatedPiste.setLength(1600);
        updatedPiste.setSlope(35);
        
        when(pisteRepository.save(any(Piste.class))).thenReturn(updatedPiste);

        // Act
        Piste result = pisteServices.updatePiste(updatedPiste);

        // Assert
        assertNotNull(result);
        assertEquals(1L, result.getNumPiste());
        assertEquals("Piste Modifiée", result.getNamePiste());
        assertEquals(Color.RED, result.getColor());
        assertEquals(1600, result.getLength());
        assertEquals(35, result.getSlope());
        
        // Verify
        verify(pisteRepository, times(1)).save(updatedPiste);
        verifyNoMoreInteractions(pisteRepository);
    }

    @Test
    @DisplayName("Récupérer une piste par ID - Succès")
    void testRetrievePiste_Success() {
        // Arrange
        when(pisteRepository.findById(1L)).thenReturn(Optional.of(testPiste));

        // Act
        Piste retrievedPiste = pisteServices.retrievePiste(1L);

        // Assert
        assertNotNull(retrievedPiste);
        assertEquals(1L, retrievedPiste.getNumPiste());
        assertEquals("Piste Test 1", retrievedPiste.getNamePiste());
        assertEquals(Color.BLUE, retrievedPiste.getColor());
        
        // Verify
        verify(pisteRepository, times(1)).findById(1L);
        verifyNoMoreInteractions(pisteRepository);
    }

    @Test
    @DisplayName("Récupérer une piste par ID - Non trouvée")
    void testRetrievePiste_NotFound() {
        // Arrange
        when(pisteRepository.findById(999L)).thenReturn(Optional.empty());

        // Act
        Piste retrievedPiste = pisteServices.retrievePiste(999L);

        // Assert
        assertNull(retrievedPiste);
        
        // Verify
        verify(pisteRepository, times(1)).findById(999L);
        verifyNoMoreInteractions(pisteRepository);
    }

    @Test
    @DisplayName("Supprimer une piste - Succès")
    void testRemovePiste_Success() {
        // Arrange
        doNothing().when(pisteRepository).deleteById(1L);

        // Act
        pisteServices.removePiste(1L);

        // Assert & Verify
        verify(pisteRepository, times(1)).deleteById(1L);
        verifyNoMoreInteractions(pisteRepository);
    }

    @Test
    @DisplayName("Test d'intégration entre ajout et récupération")
    void testIntegrationBetweenAddAndRetrieve() {
        // Arrange - Simuler l'ajout
        when(pisteRepository.save(testPiste)).thenReturn(testPiste);
        when(pisteRepository.findById(1L)).thenReturn(Optional.of(testPiste));

        // Act - Ajouter puis récupérer
        Piste savedPiste = pisteServices.addPiste(testPiste);
        Piste retrievedPiste = pisteServices.retrievePiste(savedPiste.getNumPiste());

        // Assert
        assertNotNull(savedPiste);
        assertNotNull(retrievedPiste);
        assertEquals(savedPiste.getNumPiste(), retrievedPiste.getNumPiste());
        assertEquals(savedPiste.getNamePiste(), retrievedPiste.getNamePiste());

        // Verify
        verify(pisteRepository, times(1)).save(testPiste);
        verify(pisteRepository, times(1)).findById(1L);
        verifyNoMoreInteractions(pisteRepository);
    }
}